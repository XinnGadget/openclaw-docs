---
read_when:
    - البحث عن خطوة أو علامة محددة في الإعداد الأولي
    - أتمتة الإعداد الأولي باستخدام الوضع غير التفاعلي
    - تصحيح سلوك الإعداد الأولي
sidebarTitle: Onboarding Reference
summary: 'المرجع الكامل للإعداد عبر CLI: كل خطوة، وكل علامة، وكل حقل إعدادات'
title: مرجع الإعداد الأولي
x-i18n:
    generated_at: "2026-04-07T07:22:48Z"
    model: gpt-5.4
    provider: openai
    source_hash: a142b9ec4323fabb9982d05b64375d2b4a4007dffc910acbee3a38ff871a7236
    source_path: reference/wizard.md
    workflow: 15
---

# مرجع الإعداد الأولي

هذا هو المرجع الكامل للأمر `openclaw onboard`.
للحصول على نظرة عامة عالية المستوى، راجع [الإعداد الأولي (CLI)](/ar/start/wizard).

## تفاصيل التدفق (الوضع المحلي)

<Steps>
  <Step title="اكتشاف الإعدادات الحالية">
    - إذا كان الملف `~/.openclaw/openclaw.json` موجودًا، فاختر **الاحتفاظ / التعديل / إعادة الضبط**.
    - لا تؤدي إعادة تشغيل الإعداد الأولي إلى مسح أي شيء **إلا إذا اخترت صراحةً إعادة الضبط**
      (أو مررت `--reset`).
    - تكون القيمة الافتراضية لـ CLI `--reset` هي `config+creds+sessions`؛ استخدم `--reset-scope full`
      لإزالة workspace أيضًا.
    - إذا كانت الإعدادات غير صالحة أو تحتوي على مفاتيح قديمة، يتوقف المعالج ويطلب
      منك تشغيل `openclaw doctor` قبل المتابعة.
    - تستخدم إعادة الضبط `trash` (وليس `rm` مطلقًا) وتوفر النطاقات التالية:
      - الإعدادات فقط
      - الإعدادات + بيانات الاعتماد + الجلسات
      - إعادة ضبط كاملة (تزيل workspace أيضًا)
  </Step>
  <Step title="النموذج/المصادقة">
    - **مفتاح Anthropic API**: يستخدم `ANTHROPIC_API_KEY` إذا كان موجودًا أو يطلب إدخال مفتاح، ثم يحفظه للاستخدام مع daemon.
    - **مفتاح Anthropic API**: هو خيار مساعد Anthropic المفضل في الإعداد الأولي/التهيئة.
    - **Anthropic setup-token**: ما يزال متاحًا في الإعداد الأولي/التهيئة، رغم أن OpenClaw يفضل الآن إعادة استخدام Claude CLI عند توفره.
    - **اشتراك OpenAI Code (Codex) ‏(Codex CLI)**: إذا كان الملف `~/.codex/auth.json` موجودًا، يمكن للإعداد الأولي إعادة استخدامه. وتظل بيانات اعتماد Codex CLI المعاد استخدامها مُدارة بواسطة Codex CLI؛ وعند انتهاء صلاحيتها يعيد OpenClaw قراءة ذلك المصدر أولًا، وعندما يستطيع المزود تحديثها، فإنه يكتب بيانات الاعتماد المحدّثة مرة أخرى إلى تخزين Codex بدلًا من تولي إدارتها بنفسه.
    - **اشتراك OpenAI Code (Codex) ‏(OAuth)**: تدفق عبر المتصفح؛ الصق `code#state`.
      - يضبط `agents.defaults.model` إلى `openai-codex/gpt-5.4` عندما يكون النموذج غير مضبوط أو `openai/*`.
    - **مفتاح OpenAI API**: يستخدم `OPENAI_API_KEY` إذا كان موجودًا أو يطلب إدخال مفتاح، ثم يخزنه في ملفات تعريف المصادقة.
      - يضبط `agents.defaults.model` إلى `openai/gpt-5.4` عندما يكون النموذج غير مضبوط، أو `openai/*`، أو `openai-codex/*`.
    - **مفتاح xAI (Grok) API**: يطلب `XAI_API_KEY` ويهيئ xAI كمزود نماذج.
    - **OpenCode**: يطلب `OPENCODE_API_KEY` (أو `OPENCODE_ZEN_API_KEY`، احصل عليه من https://opencode.ai/auth) ويتيح لك اختيار كتالوج Zen أو Go.
    - **Ollama**: يطلب عنوان URL الأساسي لـ Ollama، ويعرض وضع **Cloud + Local** أو **Local**، ويكتشف النماذج المتاحة، ويجلب النموذج المحلي المحدد تلقائيًا عند الحاجة.
    - مزيد من التفاصيل: [Ollama](/ar/providers/ollama)
    - **مفتاح API**: يخزن المفتاح نيابةً عنك.
    - **Vercel AI Gateway (وكيل متعدد النماذج)**: يطلب `AI_GATEWAY_API_KEY`.
    - مزيد من التفاصيل: [Vercel AI Gateway](/ar/providers/vercel-ai-gateway)
    - **Cloudflare AI Gateway**: يطلب Account ID وGateway ID و`CLOUDFLARE_AI_GATEWAY_API_KEY`.
    - مزيد من التفاصيل: [Cloudflare AI Gateway](/ar/providers/cloudflare-ai-gateway)
    - **MiniMax**: تُكتب الإعدادات تلقائيًا؛ والقيمة الافتراضية المستضافة هي `MiniMax-M2.7`.
      يستخدم إعداد مفتاح API ‏`minimax/...`، ويستخدم إعداد OAuth
      ‏`minimax-portal/...`.
    - مزيد من التفاصيل: [MiniMax](/ar/providers/minimax)
    - **StepFun**: تُكتب الإعدادات تلقائيًا لـ StepFun standard أو Step Plan على نقاط النهاية الصينية أو العالمية.
    - يتضمن Standard حاليًا `step-3.5-flash`، ويتضمن Step Plan أيضًا `step-3.5-flash-2603`.
    - مزيد من التفاصيل: [StepFun](/ar/providers/stepfun)
    - **Synthetic (متوافق مع Anthropic)**: يطلب `SYNTHETIC_API_KEY`.
    - مزيد من التفاصيل: [Synthetic](/ar/providers/synthetic)
    - **Moonshot (Kimi K2)**: تُكتب الإعدادات تلقائيًا.
    - **Kimi Coding**: تُكتب الإعدادات تلقائيًا.
    - مزيد من التفاصيل: [Moonshot AI (Kimi + Kimi Coding)](/ar/providers/moonshot)
    - **تخطي**: لم يتم إعداد أي مصادقة بعد.
    - اختر نموذجًا افتراضيًا من الخيارات المكتشفة (أو أدخل provider/model يدويًا). ولأفضل جودة وتقليل مخاطر حقن prompt، اختر أقوى نموذج متاح من الجيل الأحدث ضمن مجموعة مزوداتك.
    - يشغّل الإعداد الأولي فحصًا للنموذج ويحذر إذا كان النموذج المضبوط غير معروف أو تنقصه المصادقة.
    - يكون وضع تخزين مفتاح API افتراضيًا على قيم auth-profile نصية صريحة. استخدم `--secret-input-mode ref` لتخزين مراجع مدعومة بالبيئة بدلًا من ذلك (على سبيل المثال `keyRef: { source: "env", provider: "default", id: "OPENAI_API_KEY" }`).
    - توجد ملفات تعريف المصادقة في `~/.openclaw/agents/<agentId>/agent/auth-profiles.json` ‏(مفاتيح API + OAuth). أما `~/.openclaw/credentials/oauth.json` فهو مصدر استيراد قديم فقط.
    - مزيد من التفاصيل: [/concepts/oauth](/ar/concepts/oauth)
    <Note>
    نصيحة للخوادم/التشغيل بدون واجهة: أكمل OAuth على جهاز يحتوي على متصفح، ثم انسخ
    ملف `auth-profiles.json` الخاص بذلك الوكيل (على سبيل المثال
    `~/.openclaw/agents/<agentId>/agent/auth-profiles.json`، أو المسار المطابق
    `$OPENCLAW_STATE_DIR/...`) إلى مضيف gateway. أما `credentials/oauth.json`
    فهو مجرد مصدر استيراد قديم.
    </Note>
  </Step>
  <Step title="Workspace">
    - القيمة الافتراضية هي `~/.openclaw/workspace` ‏(قابلة للتغيير).
    - يزرع ملفات workspace اللازمة لطقس bootstrap الخاص بالوكيل.
    - دليل كامل لتخطيط workspace والنسخ الاحتياطي: [Agent workspace](/ar/concepts/agent-workspace)
  </Step>
  <Step title="Gateway">
    - المنفذ، والربط، ووضع المصادقة، وتعريض Tailscale.
    - توصية المصادقة: احتفظ بوضع **Token** حتى مع loopback حتى تضطر عملاء WS المحليون إلى المصادقة.
    - في وضع token، يوفر الإعداد التفاعلي:
      - **إنشاء/تخزين token نصي صريح** (افتراضي)
      - **استخدام SecretRef** (اختياري)
      - تعيد Quickstart استخدام SecretRefs الموجودة في `gateway.auth.token` عبر موفري `env` و`file` و`exec` لفحص onboarding/تهيئة dashboard الأولية.
      - إذا كان SecretRef مضبوطًا ولكن يتعذر حله، يفشل onboarding مبكرًا برسالة إصلاح واضحة بدلًا من إضعاف مصادقة وقت التشغيل بصمت.
    - في وضع password، يدعم الإعداد التفاعلي أيضًا التخزين النصي الصريح أو SecretRef.
    - مسار token SecretRef غير التفاعلي: `--gateway-token-ref-env <ENV_VAR>`.
      - يتطلب متغير بيئة غير فارغ في بيئة عملية onboarding.
      - لا يمكن دمجه مع `--gateway-token`.
    - عطّل المصادقة فقط إذا كنت تثق تمامًا بكل عملية محلية.
    - تتطلب عمليات الربط غير loopback المصادقة أيضًا.
  </Step>
  <Step title="القنوات">
    - [WhatsApp](/ar/channels/whatsapp): تسجيل دخول اختياري عبر QR.
    - [Telegram](/ar/channels/telegram): token للبوت.
    - [Discord](/ar/channels/discord): token للبوت.
    - [Google Chat](/ar/channels/googlechat): JSON لحساب خدمة + جمهور webhook.
    - [Mattermost](/ar/channels/mattermost) ‏(plugin): token للبوت + عنوان URL أساسي.
    - [Signal](/ar/channels/signal): تثبيت اختياري لـ `signal-cli` + إعداد الحساب.
    - [BlueBubbles](/ar/channels/bluebubbles): **موصى به لـ iMessage**؛ عنوان URL للخادم + كلمة مرور + webhook.
    - [iMessage](/ar/channels/imessage): مسار `imsg` CLI القديم + وصول إلى قاعدة البيانات.
    - أمان الرسائل الخاصة: الوضع الافتراضي هو الاقتران. ترسل أول رسالة خاصة رمزًا؛ وافق عليه عبر `openclaw pairing approve <channel> <code>` أو استخدم قوائم السماح.
  </Step>
  <Step title="البحث على الويب">
    - اختر مزودًا مدعومًا مثل Brave أو DuckDuckGo أو Exa أو Firecrawl أو Gemini أو Grok أو Kimi أو MiniMax Search أو Ollama Web Search أو Perplexity أو SearXNG أو Tavily (أو تخطَّه).
    - يمكن للمزودات المعتمدة على API استخدام متغيرات البيئة أو الإعدادات الموجودة لتهيئة سريعة؛ أما المزودات التي لا تتطلب مفاتيح فتستخدم متطلباتها الخاصة بالمزود.
    - تخطَّ هذه الخطوة باستخدام `--skip-search`.
    - الإعداد لاحقًا: `openclaw configure --section web`.
  </Step>
  <Step title="تثبيت daemon">
    - macOS: ‏LaunchAgent
      - يتطلب جلسة مستخدم مسجّل دخوله؛ أما للتشغيل بدون واجهة فاستخدم LaunchDaemon مخصصًا (غير مرفق).
    - Linux ‏(وWindows عبر WSL2): وحدة مستخدم systemd
      - يحاول الإعداد الأولي تفعيل lingering عبر `loginctl enable-linger <user>` لكي يبقى Gateway قيد التشغيل بعد تسجيل الخروج.
      - قد يطلب sudo (يكتب إلى `/var/lib/systemd/linger`)؛ ويحاول أولًا بدون sudo.
    - **اختيار وقت التشغيل:** Node ‏(موصى به؛ مطلوب لـ WhatsApp/Telegram). ولا يُوصى باستخدام Bun.
    - إذا كانت مصادقة token تتطلب token وكان `gateway.auth.token` مُدارًا بواسطة SecretRef، فإن تثبيت daemon يتحقق منه لكنه لا يحفظ قيم token النصية الصريحة المحلولة في بيانات بيئة خدمة المشرف الوصفية.
    - إذا كانت مصادقة token تتطلب token وكان token SecretRef المضبوط غير محلول، فسيتم حظر تثبيت daemon مع إرشادات عملية.
    - إذا كان كل من `gateway.auth.token` و`gateway.auth.password` مضبوطين وكان `gateway.auth.mode` غير مضبوط، فسيتم حظر تثبيت daemon حتى يتم ضبط الوضع صراحة.
  </Step>
  <Step title="فحص السلامة">
    - يبدأ Gateway ‏(إذا لزم الأمر) ويشغّل `openclaw health`.
    - نصيحة: يضيف `openclaw status --deep` فحص سلامة gateway الحي إلى مخرجات الحالة، بما في ذلك فحوصات القنوات عند الدعم (ويتطلب gateway يمكن الوصول إليه).
  </Step>
  <Step title="Skills ‏(موصى بها)">
    - يقرأ Skills المتاحة ويفحص المتطلبات.
    - يتيح لك اختيار مدير node: ‏**npm / pnpm** ‏(لا يُوصى بـ bun).
    - يثبت التبعيات الاختيارية (بعضها يستخدم Homebrew على macOS).
  </Step>
  <Step title="إنهاء">
    - ملخص + الخطوات التالية، بما في ذلك تطبيقات iOS/Android/macOS للحصول على ميزات إضافية.
  </Step>
</Steps>

<Note>
إذا لم يتم اكتشاف واجهة GUI، يطبع onboarding تعليمات إعادة توجيه منفذ SSH لـ Control UI بدلًا من فتح متصفح.
إذا كانت أصول Control UI مفقودة، يحاول onboarding بناءها؛ ويكون البديل هو `pnpm ui:build` ‏(مع تثبيت تبعيات UI تلقائيًا).
</Note>

## الوضع غير التفاعلي

استخدم `--non-interactive` لأتمتة الإعداد الأولي أو تشغيله عبر سكربتات:

```bash
openclaw onboard --non-interactive \
  --mode local \
  --auth-choice apiKey \
  --anthropic-api-key "$ANTHROPIC_API_KEY" \
  --gateway-port 18789 \
  --gateway-bind loopback \
  --install-daemon \
  --daemon-runtime node \
  --skip-skills
```

أضف `--json` للحصول على ملخص قابل للقراءة آليًا.

Gateway token SecretRef في الوضع غير التفاعلي:

```bash
export OPENCLAW_GATEWAY_TOKEN="your-token"
openclaw onboard --non-interactive \
  --mode local \
  --auth-choice skip \
  --gateway-auth token \
  --gateway-token-ref-env OPENCLAW_GATEWAY_TOKEN
```

`--gateway-token` و`--gateway-token-ref-env` متنافيان.

<Note>
لا يعني `--json` تلقائيًا الوضع غير التفاعلي. استخدم `--non-interactive` (و`--workspace`) في السكربتات.
</Note>

توجد أمثلة أوامر خاصة بالمزودين في [أتمتة CLI](/ar/start/wizard-cli-automation#provider-specific-examples).
استخدم صفحة المرجع هذه لدلالات العلامات وترتيب الخطوات.

### إضافة وكيل (غير تفاعلي)

```bash
openclaw agents add work \
  --workspace ~/.openclaw/workspace-work \
  --model openai/gpt-5.4 \
  --bind whatsapp:biz \
  --non-interactive \
  --json
```

## Gateway wizard RPC

يكشف Gateway تدفق onboarding عبر RPC ‏(`wizard.start`, `wizard.next`, `wizard.cancel`, `wizard.status`).
يمكن للعملاء (تطبيق macOS، وControl UI) عرض الخطوات بدون إعادة تنفيذ منطق onboarding.

## إعداد Signal ‏(signal-cli)

يمكن للإعداد الأولي تثبيت `signal-cli` من إصدارات GitHub:

- ينزّل أصل الإصدار المناسب.
- يخزنه ضمن `~/.openclaw/tools/signal-cli/<version>/`.
- يكتب `channels.signal.cliPath` إلى إعداداتك.

ملاحظات:

- تتطلب إصدارات JVM وجود **Java 21**.
- تُستخدم الإصدارات الأصلية عند توفرها.
- يستخدم Windows ‏WSL2؛ ويتبع تثبيت signal-cli تدفق Linux داخل WSL.

## ما الذي يكتبه المعالج

الحقول الشائعة في `~/.openclaw/openclaw.json`:

- `agents.defaults.workspace`
- `agents.defaults.model` / `models.providers` ‏(إذا تم اختيار Minimax)
- `tools.profile` ‏(يضبط onboarding المحلي افتراضيًا `"coding"` عندما يكون غير مضبوط؛ وتُحفظ القيم الصريحة الموجودة)
- `gateway.*` ‏(الوضع، والربط، والمصادقة، وtailscale)
- `session.dmScope` ‏(تفاصيل السلوك: [مرجع إعداد CLI](/ar/start/wizard-cli-reference#outputs-and-internals))
- `channels.telegram.botToken`, `channels.discord.token`, `channels.matrix.*`, `channels.signal.*`, `channels.imessage.*`
- قوائم السماح الخاصة بالقنوات (Slack/Discord/Matrix/Microsoft Teams) عند الاشتراك فيها أثناء المطالبات (ويتم تحليل الأسماء إلى معرّفات عند الإمكان).
- `skills.install.nodeManager`
  - يقبل `setup --node-manager` القيم `npm` أو `pnpm` أو `bun`.
  - لا يزال بالإمكان استخدام `yarn` يدويًا عبر ضبط `skills.install.nodeManager` مباشرة.
- `wizard.lastRunAt`
- `wizard.lastRunVersion`
- `wizard.lastRunCommit`
- `wizard.lastRunCommand`
- `wizard.lastRunMode`

يقوم `openclaw agents add` بكتابة `agents.list[]` و`bindings` الاختيارية.

توجد بيانات اعتماد WhatsApp ضمن `~/.openclaw/credentials/whatsapp/<accountId>/`.
وتُخزن الجلسات ضمن `~/.openclaw/agents/<agentId>/sessions/`.

يتم تقديم بعض القنوات على شكل plugins. وعندما تختار إحداها أثناء الإعداد،
سيطلب onboarding تثبيتها (من npm أو من مسار محلي) قبل أن يمكن تهيئتها.

## مستندات ذات صلة

- نظرة عامة على onboarding: [الإعداد الأولي (CLI)](/ar/start/wizard)
- onboarding لتطبيق macOS: ‏[Onboarding](/ar/start/onboarding)
- مرجع الإعدادات: [إعدادات Gateway](/ar/gateway/configuration)
- المزودات: [WhatsApp](/ar/channels/whatsapp)، [Telegram](/ar/channels/telegram)، [Discord](/ar/channels/discord)، [Google Chat](/ar/channels/googlechat)، [Signal](/ar/channels/signal)، [BlueBubbles](/ar/channels/bluebubbles) ‏(iMessage)، [iMessage](/ar/channels/imessage) ‏(قديم)
- Skills: ‏[Skills](/ar/tools/skills)، [إعدادات Skills](/ar/tools/skills-config)
