---
read_when:
    - تمكين تحويل النص إلى كلام للردود
    - تهيئة موفري TTS أو الحدود
    - استخدام أوامر `/tts`
summary: تحويل النص إلى كلام (TTS) للردود الصادرة
title: تحويل النص إلى كلام
x-i18n:
    generated_at: "2026-04-16T07:17:55Z"
    model: gpt-5.4
    provider: openai
    source_hash: de7c1dc8831c1ba307596afd48cb4d36f844724887a13b17e35f41ef5174a86f
    source_path: tools/tts.md
    workflow: 15
---

# تحويل النص إلى كلام (TTS)

يمكن لـ OpenClaw تحويل الردود الصادرة إلى صوت باستخدام ElevenLabs أو Google Gemini أو Microsoft أو MiniMax أو OpenAI.
ويعمل ذلك في أي مكان يستطيع OpenClaw فيه إرسال صوت.

## الخدمات المدعومة

- **ElevenLabs** (موفر أساسي أو احتياطي)
- **Google Gemini** (موفر أساسي أو احتياطي؛ يستخدم Gemini API TTS)
- **Microsoft** (موفر أساسي أو احتياطي؛ يستخدم التنفيذ المضمّن الحالي `node-edge-tts`)
- **MiniMax** (موفر أساسي أو احتياطي؛ يستخدم واجهة T2A v2 API)
- **OpenAI** (موفر أساسي أو احتياطي؛ ويُستخدم أيضًا للملخصات)

### ملاحظات حول Microsoft speech

يستخدم موفر Microsoft speech المضمّن حاليًا خدمة TTS العصبية عبر الإنترنت من Microsoft Edge
من خلال مكتبة `node-edge-tts`. وهي خدمة مستضافة (وليست
محلية)، وتستخدم نقاط نهاية Microsoft، ولا تتطلب مفتاح API.
يتيح `node-edge-tts` خيارات لتهيئة النطق وتنسيقات الإخراج، لكن
ليست كل الخيارات مدعومة من الخدمة. ولا يزال الإدخال الخاص
بالتهيئة القديمة والتوجيهات الذي يستخدم `edge` يعمل، ويجري تطبيعه إلى `microsoft`.

نظرًا لأن هذا المسار يعتمد على خدمة ويب عامة من دون SLA أو حصة منشورة،
فتعامل معه على أنه أفضل جهد. إذا كنت بحاجة إلى حدود مضمونة ودعم، فاستخدم OpenAI
أو ElevenLabs.

## المفاتيح الاختيارية

إذا كنت تريد OpenAI أو ElevenLabs أو Google Gemini أو MiniMax:

- `ELEVENLABS_API_KEY` (أو `XI_API_KEY`)
- `GEMINI_API_KEY` (أو `GOOGLE_API_KEY`)
- `MINIMAX_API_KEY`
- `OPENAI_API_KEY`

لا تتطلب Microsoft speech **مفتاح API**.

إذا جرى إعداد عدة موفرين، فسيُستخدم الموفر المحدد أولًا وستكون الموفرات الأخرى خيارات احتياطية.
يستخدم التلخيص التلقائي `summaryModel` المُعدّ (أو `agents.defaults.model.primary`)،
لذلك يجب أيضًا أن يكون هذا الموفر موثّقًا إذا فعّلت الملخصات.

## روابط الخدمات

- [دليل OpenAI لتحويل النص إلى كلام](https://platform.openai.com/docs/guides/text-to-speech)
- [مرجع OpenAI Audio API](https://platform.openai.com/docs/api-reference/audio)
- [تحويل النص إلى كلام في ElevenLabs](https://elevenlabs.io/docs/api-reference/text-to-speech)
- [المصادقة في ElevenLabs](https://elevenlabs.io/docs/api-reference/authentication)
- [واجهة MiniMax T2A v2 API](https://platform.minimaxi.com/document/T2A%20V2)
- [node-edge-tts](https://github.com/SchneeHertz/node-edge-tts)
- [تنسيقات إخراج Microsoft Speech](https://learn.microsoft.com/azure/ai-services/speech-service/rest-text-to-speech#audio-outputs)

## هل هو مفعّل افتراضيًا؟

لا. يكون Auto‑TTS **متوقفًا** افتراضيًا. فعّله في الإعدادات باستخدام
`messages.tts.auto` أو محليًا باستخدام `/tts on`.

عندما لا تكون `messages.tts.provider` معيّنة، يختار OpenClaw أول
موفر speech مُعدّ وفق ترتيب الاختيار التلقائي في السجل.

## التهيئة

توجد تهيئة TTS ضمن `messages.tts` في `openclaw.json`.
المخطط الكامل موجود في [تهيئة Gateway](/ar/gateway/configuration).

### الحد الأدنى من التهيئة (تمكين + موفر)

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

### OpenAI كأساسي مع ElevenLabs كاحتياطي

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

### Microsoft كأساسي (من دون مفتاح API)

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

### MiniMax كأساسي

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

### Google Gemini كأساسي

```json5
{
  messages: {
    tts: {
      auto: "always",
      provider: "google",
      providers: {
        google: {
          apiKey: "gemini_api_key",
          model: "gemini-3.1-flash-tts-preview",
          voiceName: "Kore",
        },
      },
    },
  },
}
```

يستخدم Google Gemini TTS مسار مفتاح Gemini API. يكون مفتاح API من Google Cloud Console
المقيّد على Gemini API صالحًا هنا، وهو نفس نمط المفتاح المستخدم
من قبل موفر إنشاء الصور المضمّن من Google. ترتيب الاستيفاء هو
`messages.tts.providers.google.apiKey` -> `models.providers.google.apiKey` ->
`GEMINI_API_KEY` -> `GOOGLE_API_KEY`.

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

- `auto`: وضع Auto‑TTS (`off` أو `always` أو `inbound` أو `tagged`).
  - يرسل `inbound` الصوت فقط بعد رسالة صوتية واردة.
  - يرسل `tagged` الصوت فقط عندما يتضمن الرد توجيهات `[[tts:key=value]]` أو كتلة `[[tts:text]]...[[/tts:text]]`.
- `enabled`: مفتاح تبديل قديم (يقوم doctor بترحيله إلى `auto`).
- `mode`: `"final"` (الافتراضي) أو `"all"` (يتضمن ردود الأدوات/الكتل).
- `provider`: معرّف موفر speech مثل `"elevenlabs"` أو `"google"` أو `"microsoft"` أو `"minimax"` أو `"openai"` (يكون الاحتياطي تلقائيًا).
- إذا لم يتم تعيين `provider`، يستخدم OpenClaw أول موفر speech مُعدّ وفق ترتيب الاختيار التلقائي في السجل.
- لا يزال `provider: "edge"` القديم يعمل ويُطبَّع إلى `microsoft`.
- `summaryModel`: نموذج منخفض التكلفة اختياري للتلخيص التلقائي؛ والقيمة الافتراضية هي `agents.defaults.model.primary`.
  - يقبل `provider/model` أو اسمًا مستعارًا لنموذج مُعدّ.
- `modelOverrides`: السماح للنموذج بإخراج توجيهات TTS (مفعّل افتراضيًا).
  - تكون القيمة الافتراضية لـ `allowProvider` هي `false` (التبديل بين الموفرين يتطلب التفعيل صراحةً).
- `providers.<id>`: إعدادات خاصة بالموفر ومفهرسة بمعرّف موفر speech.
- كتل الموفر القديمة المباشرة (`messages.tts.openai` و`messages.tts.elevenlabs` و`messages.tts.microsoft` و`messages.tts.edge`) تُرحَّل تلقائيًا إلى `messages.tts.providers.<id>` عند التحميل.
- `maxTextLength`: حد أقصى صارم لإدخال TTS (أحرف). يفشل `/tts audio` إذا تم تجاوزه.
- `timeoutMs`: مهلة انتهاء الطلب (مللي ثانية).
- `prefsPath`: تجاوز مسار JSON المحلي للتفضيلات (الموفر/الحد/الملخص).
- تعود قيم `apiKey` إلى متغيرات البيئة (`ELEVENLABS_API_KEY`/`XI_API_KEY` و`GEMINI_API_KEY`/`GOOGLE_API_KEY` و`MINIMAX_API_KEY` و`OPENAI_API_KEY`).
- `providers.elevenlabs.baseUrl`: تجاوز عنوان URL الأساسي لـ ElevenLabs API.
- `providers.openai.baseUrl`: تجاوز نقطة نهاية OpenAI TTS.
  - ترتيب الاستيفاء: `messages.tts.providers.openai.baseUrl` -> `OPENAI_TTS_BASE_URL` -> `https://api.openai.com/v1`
  - تُعامل القيم غير الافتراضية على أنها نقاط نهاية TTS متوافقة مع OpenAI، لذلك تُقبل أسماء النماذج والأصوات المخصصة.
- `providers.elevenlabs.voiceSettings`:
  - `stability` و`similarityBoost` و`style`: `0..1`
  - `useSpeakerBoost`: `true|false`
  - `speed`: `0.5..2.0` (1.0 = عادي)
- `providers.elevenlabs.applyTextNormalization`: ‏`auto|on|off`
- `providers.elevenlabs.languageCode`: رمز ISO 639-1 من حرفين (مثل `en` أو `de`)
- `providers.elevenlabs.seed`: عدد صحيح `0..4294967295` (حتمية بأفضل جهد)
- `providers.minimax.baseUrl`: تجاوز عنوان URL الأساسي لـ MiniMax API (الافتراضي `https://api.minimax.io`، ومتغير البيئة: `MINIMAX_API_HOST`).
- `providers.minimax.model`: نموذج TTS (الافتراضي `speech-2.8-hd`، ومتغير البيئة: `MINIMAX_TTS_MODEL`).
- `providers.minimax.voiceId`: معرّف الصوت (الافتراضي `English_expressive_narrator`، ومتغير البيئة: `MINIMAX_TTS_VOICE_ID`).
- `providers.minimax.speed`: سرعة التشغيل `0.5..2.0` (الافتراضي 1.0).
- `providers.minimax.vol`: مستوى الصوت `(0, 10]` (الافتراضي 1.0؛ ويجب أن يكون أكبر من 0).
- `providers.minimax.pitch`: تغيير النغمة `-12..12` (الافتراضي 0).
- `providers.google.model`: نموذج Gemini TTS (الافتراضي `gemini-3.1-flash-tts-preview`).
- `providers.google.voiceName`: اسم صوت Gemini المضمّن مسبقًا (الافتراضي `Kore`؛ كما يُقبل `voice` أيضًا).
- `providers.google.baseUrl`: تجاوز عنوان URL الأساسي لـ Gemini API. لا يُقبل إلا `https://generativelanguage.googleapis.com`.
  - إذا تم حذف `messages.tts.providers.google.apiKey`، يمكن لـ TTS إعادة استخدام `models.providers.google.apiKey` قبل الرجوع إلى متغيرات البيئة.
- `providers.microsoft.enabled`: السماح باستخدام Microsoft speech (الافتراضي `true`؛ بدون مفتاح API).
- `providers.microsoft.voice`: اسم الصوت العصبي من Microsoft (مثل `en-US-MichelleNeural`).
- `providers.microsoft.lang`: رمز اللغة (مثل `en-US`).
- `providers.microsoft.outputFormat`: تنسيق إخراج Microsoft (مثل `audio-24khz-48kbitrate-mono-mp3`).
  - راجع تنسيقات إخراج Microsoft Speech لمعرفة القيم الصالحة؛ فليست كل التنسيقات مدعومة من النقل المضمّن المعتمد على Edge.
- `providers.microsoft.rate` / `providers.microsoft.pitch` / `providers.microsoft.volume`: سلاسل نسب مئوية (مثل `+10%` و`-5%`).
- `providers.microsoft.saveSubtitles`: كتابة ترجمات JSON إلى جانب ملف الصوت.
- `providers.microsoft.proxy`: عنوان URL للوكيل لطلبات Microsoft speech.
- `providers.microsoft.timeoutMs`: تجاوز مهلة انتهاء الطلب (مللي ثانية).
- `edge.*`: اسم مستعار قديم لإعدادات Microsoft نفسها.

## تجاوزات يقودها النموذج (مفعّلة افتراضيًا)

افتراضيًا، **يمكن** للنموذج إخراج توجيهات TTS لرد واحد.
عندما تكون `messages.tts.auto` مضبوطة على `tagged`، تكون هذه التوجيهات مطلوبة لتفعيل الصوت.

عند التفعيل، يمكن للنموذج إخراج توجيهات `[[tts:...]]` لتجاوز إعداد الصوت
لرد واحد، بالإضافة إلى كتلة اختيارية `[[tts:text]]...[[/tts:text]]`
لتوفير وسوم تعبيرية (ضحك، إشارات غناء، وما إلى ذلك) يجب أن تظهر فقط في
الصوت.

يتم تجاهل توجيهات `provider=...` ما لم تكن `modelOverrides.allowProvider: true`.

مثال على حمولة رد:

```
Here you go.

[[tts:voiceId=pMsXgVXv3BLzUgSXRplE model=eleven_v3 speed=1.1]]
[[tts:text]](laughs) Read the song once more.[[/tts:text]]
```

مفاتيح التوجيه المتاحة (عند التفعيل):

- `provider` (معرّف موفر speech مسجّل، مثل `openai` أو `elevenlabs` أو `google` أو `minimax` أو `microsoft`؛ ويتطلب `allowProvider: true`)
- `voice` (صوت OpenAI)، أو `voiceName` / `voice_name` / `google_voice` (صوت Google)، أو `voiceId` (ElevenLabs / MiniMax)
- `model` (نموذج OpenAI TTS أو معرّف نموذج ElevenLabs أو نموذج MiniMax) أو `google_model` (نموذج Google TTS)
- `stability` و`similarityBoost` و`style` و`speed` و`useSpeakerBoost`
- `vol` / `volume` (مستوى صوت MiniMax، من 0 إلى 10)
- `pitch` (نغمة MiniMax، من -12 إلى 12)
- `applyTextNormalization` (`auto|on|off`)
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

قائمة سماح اختيارية (تمكين التبديل بين الموفرين مع الإبقاء على بقية عناصر الضبط قابلة للتهيئة):

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

## تفضيلات لكل مستخدم

تكتب أوامر الشرطة المائلة تجاوزات محلية إلى `prefsPath` (الافتراضي:
`~/.openclaw/settings/tts.json`، ويمكن التجاوز باستخدام `OPENCLAW_TTS_PREFS` أو
`messages.tts.prefsPath`).

الحقول المخزنة:

- `enabled`
- `provider`
- `maxLength` (حد التلخيص؛ الافتراضي 1500 حرفًا)
- `summarize` (الافتراضي `true`)

تتجاوز هذه الحقول `messages.tts.*` على ذلك المضيف.

## تنسيقات الإخراج (ثابتة)

- **Feishu / Matrix / Telegram / WhatsApp**: رسالة صوتية Opus (`opus_48000_64` من ElevenLabs، و`opus` من OpenAI).
  - يُعد 48kHz / 64kbps توازنًا جيدًا للرسائل الصوتية.
- **القنوات الأخرى**: MP3 (`mp3_44100_128` من ElevenLabs، و`mp3` من OpenAI).
  - يُعد 44.1kHz / 128kbps التوازن الافتراضي لوضوح الكلام.
- **MiniMax**: ‏MP3 (نموذج `speech-2.8-hd`، ومعدل عينات 32kHz). لا يدعم تنسيق الملاحظات الصوتية أصلاً؛ استخدم OpenAI أو ElevenLabs إذا كنت بحاجة إلى رسائل صوتية Opus مضمونة.
- **Google Gemini**: يعيد Gemini API TTS بيانات PCM خام بمعدل 24kHz. يغلّفها OpenClaw بصيغة WAV لمرفقات الصوت، ويعيد PCM مباشرةً لـ Talk/telephony. لا يدعم هذا المسار تنسيق ملاحظات Opus الصوتية الأصلي.
- **Microsoft**: يستخدم `microsoft.outputFormat` (الافتراضي `audio-24khz-48kbitrate-mono-mp3`).
  - يقبل النقل المضمّن قيمة `outputFormat`، لكن ليست كل التنسيقات متاحة من الخدمة.
  - تتبع قيم تنسيق الإخراج تنسيقات إخراج Microsoft Speech (بما في ذلك Ogg/WebM Opus).
  - يقبل Telegram `sendVoice` تنسيقات OGG/MP3/M4A؛ استخدم OpenAI/ElevenLabs إذا كنت بحاجة
    إلى رسائل صوتية Opus مضمونة.
  - إذا فشل تنسيق إخراج Microsoft المُعدّ، يعيد OpenClaw المحاولة باستخدام MP3.

تكون تنسيقات إخراج OpenAI/ElevenLabs ثابتة بحسب القناة (انظر أعلاه).

## سلوك Auto-TTS

عند التفعيل، يقوم OpenClaw بما يلي:

- يتخطى TTS إذا كان الرد يحتوي بالفعل على وسائط أو توجيه `MEDIA:`.
- يتخطى الردود القصيرة جدًا (أقل من 10 أحرف).
- يلخّص الردود الطويلة عند التفعيل باستخدام `agents.defaults.model.primary` (أو `summaryModel`).
- يرفق الصوت المُنشأ بالرد.

إذا تجاوز الرد `maxLength` وكان التلخيص متوقفًا (أو لم يوجد مفتاح API لـ
نموذج التلخيص)،
فسيتم تخطي الصوت وسيُرسل الرد النصي العادي.

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
راجع [أوامر الشرطة المائلة](/ar/tools/slash-commands) لمعرفة تفاصيل التفعيل.

ملاحظة Discord: الأمر `/tts` هو أمر مضمّن في Discord، لذلك يسجّل OpenClaw
`/voice` باعتباره الأمر الأصلي هناك. وما يزال النص `/tts ...` يعمل.

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

- تتطلب الأوامر مُرسِلًا مخوّلًا (وما تزال قواعد allowlist/owner سارية).
- يجب تفعيل `commands.text` أو تسجيل الأوامر الأصلية.
- تقبل تهيئة `messages.tts.auto` القيم `off|always|inbound|tagged`.
- يكتب `/tts on` تفضيل TTS المحلي إلى `always`؛ ويكتب `/tts off` إلى `off`.
- استخدم التهيئة عندما تريد القيم الافتراضية `inbound` أو `tagged`.
- يتم تخزين `limit` و`summary` في التفضيلات المحلية، وليس في التهيئة الرئيسية.
- ينشئ `/tts audio` ردًا صوتيًا لمرة واحدة (ولا يفعّل TTS).
- يتضمن `/tts status` إظهارًا للاحتياطي في آخر محاولة:
  - نجاح مع احتياطي: `Fallback: <primary> -> <used>` بالإضافة إلى `Attempts: ...`
  - فشل: `Error: ...` بالإضافة إلى `Attempts: ...`
  - تشخيصات مفصلة: `Attempt details: provider:outcome(reasonCode) latency`
- تتضمن حالات فشل OpenAI وElevenLabs API الآن تفاصيل خطأ الموفر المُحللة ومعرّف الطلب (عند إرجاعه من الموفر)، ويظهر ذلك في أخطاء/سجلات TTS.

## أداة الوكيل

تقوم أداة `tts` بتحويل النص إلى كلام وتُرجع مرفقًا صوتيًا من أجل
تسليم الرد. عندما تكون القناة Feishu أو Matrix أو Telegram أو WhatsApp،
يُسلَّم الصوت كرسالة صوتية بدلًا من مرفق ملف.

## Gateway RPC

طرائق Gateway:

- `tts.status`
- `tts.enable`
- `tts.disable`
- `tts.convert`
- `tts.setProvider`
- `tts.providers`
