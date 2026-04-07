---
read_when:
    - تحتاج إلى استدعاء مساعدات النواة من plugin (TTS وSTT وتوليد الصور والبحث على الويب وsubagent)
    - تريد فهم ما الذي يكشفه api.runtime
    - أنت تصل إلى مساعدات التهيئة أو الوكيل أو الوسائط من شيفرة plugin
sidebarTitle: Runtime Helpers
summary: api.runtime -- مساعدات وقت التشغيل المحقونة المتاحة لـ plugins
title: مساعدات وقت تشغيل plugin
x-i18n:
    generated_at: "2026-04-07T07:20:51Z"
    model: gpt-5.4
    provider: openai
    source_hash: acb9e56678e9ed08d0998dfafd7cd1982b592be5bc34d9e2d2c1f70274f8f248
    source_path: plugins/sdk-runtime.md
    workflow: 15
---

# مساعدات وقت تشغيل plugin

مرجع لكائن `api.runtime` المحقون في كل plugin أثناء
التسجيل. استخدم هذه المساعدات بدلًا من استيراد الأجزاء الداخلية للمضيف مباشرة.

<Tip>
  **تبحث عن شرح عملي؟** راجع [Plugins القنوات](/ar/plugins/sdk-channel-plugins)
  أو [Provider Plugins](/ar/plugins/sdk-provider-plugins) للحصول على أدلة خطوة بخطوة
  تعرض هذه المساعدات في سياقها.
</Tip>

```typescript
register(api) {
  const runtime = api.runtime;
}
```

## مساحات الأسماء في وقت التشغيل

### `api.runtime.agent`

هوية الوكيل، والدلائل، وإدارة الجلسات.

```typescript
// تحليل دليل العمل الخاص بالوكيل
const agentDir = api.runtime.agent.resolveAgentDir(cfg);

// تحليل مساحة عمل الوكيل
const workspaceDir = api.runtime.agent.resolveAgentWorkspaceDir(cfg);

// الحصول على هوية الوكيل
const identity = api.runtime.agent.resolveAgentIdentity(cfg);

// الحصول على مستوى التفكير الافتراضي
const thinking = api.runtime.agent.resolveThinkingDefault(cfg, provider, model);

// الحصول على مهلة الوكيل
const timeoutMs = api.runtime.agent.resolveAgentTimeoutMs(cfg);

// التأكد من وجود مساحة العمل
await api.runtime.agent.ensureAgentWorkspace(cfg);

// تشغيل وكيل Pi مضمن
const agentDir = api.runtime.agent.resolveAgentDir(cfg);
const result = await api.runtime.agent.runEmbeddedPiAgent({
  sessionId: "my-plugin:task-1",
  runId: crypto.randomUUID(),
  sessionFile: path.join(agentDir, "sessions", "my-plugin-task-1.jsonl"),
  workspaceDir: api.runtime.agent.resolveAgentWorkspaceDir(cfg),
  prompt: "Summarize the latest changes",
  timeoutMs: api.runtime.agent.resolveAgentTimeoutMs(cfg),
});
```

**مساعدات مخزن الجلسات** موجودة تحت `api.runtime.agent.session`:

```typescript
const storePath = api.runtime.agent.session.resolveStorePath(cfg);
const store = api.runtime.agent.session.loadSessionStore(cfg);
await api.runtime.agent.session.saveSessionStore(cfg, store);
const filePath = api.runtime.agent.session.resolveSessionFilePath(cfg, sessionId);
```

### `api.runtime.agent.defaults`

ثوابت النموذج والموفر الافتراضية:

```typescript
const model = api.runtime.agent.defaults.model; // مثال: "anthropic/claude-sonnet-4-6"
const provider = api.runtime.agent.defaults.provider; // مثال: "anthropic"
```

### `api.runtime.subagent`

شغّل عمليات subagent في الخلفية وأدرها.

```typescript
// بدء تشغيل subagent
const { runId } = await api.runtime.subagent.run({
  sessionKey: "agent:main:subagent:search-helper",
  message: "Expand this query into focused follow-up searches.",
  provider: "openai", // تجاوز اختياري
  model: "gpt-4.1-mini", // تجاوز اختياري
  deliver: false,
});

// الانتظار حتى الاكتمال
const result = await api.runtime.subagent.waitForRun({ runId, timeoutMs: 30000 });

// قراءة رسائل الجلسة
const { messages } = await api.runtime.subagent.getSessionMessages({
  sessionKey: "agent:main:subagent:search-helper",
  limit: 10,
});

// حذف جلسة
await api.runtime.subagent.deleteSession({
  sessionKey: "agent:main:subagent:search-helper",
});
```

<Warning>
  تتطلب تجاوزات النموذج (`provider`/`model`) موافقة المشغّل عبر
  `plugins.entries.<id>.subagent.allowModelOverride: true` في التهيئة.
  ما تزال plugins غير الموثوقة قادرة على تشغيل subagents، لكن طلبات التجاوز تُرفض.
</Warning>

### `api.runtime.taskFlow`

اربط وقت تشغيل Task Flow بمفتاح جلسة OpenClaw موجود أو بسياق أداة موثوق،
ثم أنشئ Task Flows وأدرها دون تمرير مالك في كل استدعاء.

```typescript
const taskFlow = api.runtime.taskFlow.fromToolContext(ctx);

const created = taskFlow.createManaged({
  controllerId: "my-plugin/review-batch",
  goal: "Review new pull requests",
});

const child = taskFlow.runTask({
  flowId: created.flowId,
  runtime: "acp",
  childSessionKey: "agent:main:subagent:reviewer",
  task: "Review PR #123",
  status: "running",
  startedAt: Date.now(),
});

const waiting = taskFlow.setWaiting({
  flowId: created.flowId,
  expectedRevision: created.revision,
  currentStep: "await-human-reply",
  waitJson: { kind: "reply", channel: "telegram" },
});
```

استخدم `bindSession({ sessionKey, requesterOrigin })` عندما يكون لديك بالفعل
مفتاح جلسة OpenClaw موثوق من طبقة الربط الخاصة بك. لا تربط انطلاقًا من إدخال مستخدم خام.

### `api.runtime.tts`

تحويل النص إلى كلام.

```typescript
// TTS قياسي
const clip = await api.runtime.tts.textToSpeech({
  text: "Hello from OpenClaw",
  cfg: api.config,
});

// TTS محسّن للاتصالات الهاتفية
const telephonyClip = await api.runtime.tts.textToSpeechTelephony({
  text: "Hello from OpenClaw",
  cfg: api.config,
});

// عرض الأصوات المتاحة
const voices = await api.runtime.tts.listVoices({
  provider: "elevenlabs",
  cfg: api.config,
});
```

يستخدم تهيئة `messages.tts` الأساسية واختيار الموفّر. ويعيد مخزنًا مؤقتًا
لصوت PCM + معدل العينة.

### `api.runtime.mediaUnderstanding`

تحليل الصور والصوت والفيديو.

```typescript
// وصف صورة
const image = await api.runtime.mediaUnderstanding.describeImageFile({
  filePath: "/tmp/inbound-photo.jpg",
  cfg: api.config,
  agentDir: "/tmp/agent",
});

// تفريغ صوتي
const { text } = await api.runtime.mediaUnderstanding.transcribeAudioFile({
  filePath: "/tmp/inbound-audio.ogg",
  cfg: api.config,
  mime: "audio/ogg", // اختياري، عندما لا يمكن استنتاج MIME
});

// وصف فيديو
const video = await api.runtime.mediaUnderstanding.describeVideoFile({
  filePath: "/tmp/inbound-video.mp4",
  cfg: api.config,
});

// تحليل ملف عام
const result = await api.runtime.mediaUnderstanding.runFile({
  filePath: "/tmp/inbound-file.pdf",
  cfg: api.config,
});
```

يعيد `{ text: undefined }` عندما لا يُنتَج أي خرج (مثلًا عند تخطي الإدخال).

<Info>
  يبقى `api.runtime.stt.transcribeAudioFile(...)` اسمًا مستعارًا للتوافق
  مع `api.runtime.mediaUnderstanding.transcribeAudioFile(...)`.
</Info>

### `api.runtime.imageGeneration`

توليد الصور.

```typescript
const result = await api.runtime.imageGeneration.generate({
  prompt: "A robot painting a sunset",
  cfg: api.config,
});

const providers = api.runtime.imageGeneration.listProviders({ cfg: api.config });
```

### `api.runtime.webSearch`

البحث على الويب.

```typescript
const providers = api.runtime.webSearch.listProviders({ config: api.config });

const result = await api.runtime.webSearch.search({
  config: api.config,
  args: { query: "OpenClaw plugin SDK", count: 5 },
});
```

### `api.runtime.media`

أدوات الوسائط منخفضة المستوى.

```typescript
const webMedia = await api.runtime.media.loadWebMedia(url);
const mime = await api.runtime.media.detectMime(buffer);
const kind = api.runtime.media.mediaKindFromMime("image/jpeg"); // "image"
const isVoice = api.runtime.media.isVoiceCompatibleAudio(filePath);
const metadata = await api.runtime.media.getImageMetadata(filePath);
const resized = await api.runtime.media.resizeToJpeg(buffer, { maxWidth: 800 });
```

### `api.runtime.config`

تحميل التهيئة وكتابتها.

```typescript
const cfg = await api.runtime.config.loadConfig();
await api.runtime.config.writeConfigFile(cfg);
```

### `api.runtime.system`

أدوات على مستوى النظام.

```typescript
await api.runtime.system.enqueueSystemEvent(event);
api.runtime.system.requestHeartbeatNow();
const output = await api.runtime.system.runCommandWithTimeout(cmd, args, opts);
const hint = api.runtime.system.formatNativeDependencyHint(pkg);
```

### `api.runtime.events`

اشتراكات الأحداث.

```typescript
api.runtime.events.onAgentEvent((event) => {
  /* ... */
});
api.runtime.events.onSessionTranscriptUpdate((update) => {
  /* ... */
});
```

### `api.runtime.logging`

التسجيل.

```typescript
const verbose = api.runtime.logging.shouldLogVerbose();
const childLogger = api.runtime.logging.getChildLogger({ plugin: "my-plugin" }, { level: "debug" });
```

### `api.runtime.modelAuth`

تحليل مصادقة النموذج والموفّر.

```typescript
const auth = await api.runtime.modelAuth.getApiKeyForModel({ model, cfg });
const providerAuth = await api.runtime.modelAuth.resolveApiKeyForProvider({
  provider: "openai",
  cfg,
});
```

### `api.runtime.state`

تحليل دليل الحالة.

```typescript
const stateDir = api.runtime.state.resolveStateDir();
```

### `api.runtime.tools`

مصانع أدوات الذاكرة وCLI.

```typescript
const getTool = api.runtime.tools.createMemoryGetTool(/* ... */);
const searchTool = api.runtime.tools.createMemorySearchTool(/* ... */);
api.runtime.tools.registerMemoryCli(/* ... */);
```

### `api.runtime.channel`

مساعدات وقت التشغيل الخاصة بالقناة (متاحة عند تحميل plugin قناة).

`api.runtime.channel.mentions` هو سطح سياسة الذكر المشتركة للرسائل الواردة
من أجل plugins القنوات المضمّنة التي تستخدم حقن وقت التشغيل:

```typescript
const mentionMatch = api.runtime.channel.mentions.matchesMentionWithExplicit(text, {
  mentionRegexes,
  mentionPatterns,
});

const decision = api.runtime.channel.mentions.resolveInboundMentionDecision({
  facts: {
    canDetectMention: true,
    wasMentioned: mentionMatch.matched,
    implicitMentionKinds: api.runtime.channel.mentions.implicitMentionKindWhen(
      "reply_to_bot",
      isReplyToBot,
    ),
  },
  policy: {
    isGroup,
    requireMention,
    allowTextCommands,
    hasControlCommand,
    commandAuthorized,
  },
});
```

مساعدات الذكر المتاحة:

- `buildMentionRegexes`
- `matchesMentionPatterns`
- `matchesMentionWithExplicit`
- `implicitMentionKindWhen`
- `resolveInboundMentionDecision`

لا يكشف `api.runtime.channel.mentions` عمدًا عن مساعدات التوافق الأقدم
`resolveMentionGating*`. فضّل المسار الموحّد
`{ facts, policy }`.

## تخزين مراجع وقت التشغيل

استخدم `createPluginRuntimeStore` لتخزين مرجع وقت التشغيل لاستخدامه خارج
نداء `register`:

```typescript
import { createPluginRuntimeStore } from "openclaw/plugin-sdk/runtime-store";
import type { PluginRuntime } from "openclaw/plugin-sdk/runtime-store";

const store = createPluginRuntimeStore<PluginRuntime>("my-plugin runtime not initialized");

// في نقطة الدخول الخاصة بك
export default defineChannelPluginEntry({
  id: "my-plugin",
  name: "My Plugin",
  description: "Example",
  plugin: myPlugin,
  setRuntime: store.setRuntime,
});

// في ملفات أخرى
export function getRuntime() {
  return store.getRuntime(); // يطرح خطأ إذا لم تتم التهيئة
}

export function tryGetRuntime() {
  return store.tryGetRuntime(); // يعيد null إذا لم تتم التهيئة
}
```

## حقول `api` الأخرى على المستوى الأعلى

إلى جانب `api.runtime`، يوفر كائن API أيضًا:

| الحقل                    | النوع                     | الوصف                                                                                     |
| ------------------------ | ------------------------- | ----------------------------------------------------------------------------------------- |
| `api.id`                 | `string`                  | معرّف plugin                                                                               |
| `api.name`               | `string`                  | اسم عرض plugin                                                                             |
| `api.config`             | `OpenClawConfig`          | لقطة التهيئة الحالية (لقطة وقت التشغيل النشطة داخل الذاكرة عند توفرها)                    |
| `api.pluginConfig`       | `Record<string, unknown>` | تهيئة خاصة بـ plugin من `plugins.entries.<id>.config`                                      |
| `api.logger`             | `PluginLogger`            | مسجّل ضمن النطاق (`debug` و`info` و`warn` و`error`)                                        |
| `api.registrationMode`   | `PluginRegistrationMode`  | وضع التحميل الحالي؛ وتمثل `"setup-runtime"` نافذة بدء التشغيل/الإعداد الخفيفة قبل نقطة الدخول الكاملة |
| `api.resolvePath(input)` | `(string) => string`      | تحليل مسار نسبةً إلى جذر plugin                                                             |

## ذو صلة

- [نظرة عامة على SDK](/ar/plugins/sdk-overview) -- مرجع المسارات الفرعية
- [نقاط دخول SDK](/ar/plugins/sdk-entrypoints) -- خيارات `definePluginEntry`
- [الأجزاء الداخلية لـ plugin](/ar/plugins/architecture) -- نموذج الإمكانات والسجل
