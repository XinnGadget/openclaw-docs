---
read_when:
    - أنت تؤتمت التهيئة في نصوص برمجية أو في CI
    - تحتاج إلى أمثلة غير تفاعلية لمزوّدين محددين
sidebarTitle: CLI automation
summary: تهيئة موجّهة بالنصوص البرمجية وإعداد الوكلاء لـ CLI في OpenClaw
title: أتمتة CLI
x-i18n:
    generated_at: "2026-04-07T07:22:23Z"
    model: gpt-5.4
    provider: openai
    source_hash: bca2dd6e482a16b27284fc76319e936e8df0ff5558134827c19f6875436cc652
    source_path: start/wizard-cli-automation.md
    workflow: 15
---

# أتمتة CLI

استخدم `--non-interactive` لأتمتة `openclaw onboard`.

<Note>
لا يعني `--json` وضعًا غير تفاعلي. استخدم `--non-interactive` (و `--workspace`) في النصوص البرمجية.
</Note>

## مثال أساسي غير تفاعلي

```bash
openclaw onboard --non-interactive \
  --mode local \
  --auth-choice apiKey \
  --anthropic-api-key "$ANTHROPIC_API_KEY" \
  --secret-input-mode plaintext \
  --gateway-port 18789 \
  --gateway-bind loopback \
  --install-daemon \
  --daemon-runtime node \
  --skip-skills
```

أضف `--json` للحصول على ملخص قابل للقراءة آليًا.

استخدم `--secret-input-mode ref` لتخزين مراجع مدعومة بمتغيرات البيئة في ملفات تعريف المصادقة بدلًا من القيم النصية الصريحة.
يتوفر في تدفق التهيئة اختيار تفاعلي بين مراجع البيئة ومراجع المزوّد المهيأة (`file` أو `exec`).

في وضع `ref` غير التفاعلي، يجب أن تكون متغيرات بيئة المزوّد مضبوطة في بيئة العملية.
إن تمرير أعلام مفاتيح مضمنة من دون متغير البيئة المطابق يؤدي الآن إلى فشل سريع.

مثال:

```bash
openclaw onboard --non-interactive \
  --mode local \
  --auth-choice openai-api-key \
  --secret-input-mode ref \
  --accept-risk
```

## أمثلة خاصة بالمزوّد

<AccordionGroup>
  <Accordion title="مثال على مفتاح API لـ Anthropic">
    ```bash
    openclaw onboard --non-interactive \
      --mode local \
      --auth-choice apiKey \
      --anthropic-api-key "$ANTHROPIC_API_KEY" \
      --gateway-port 18789 \
      --gateway-bind loopback
    ```
  </Accordion>
  <Accordion title="مثال Gemini">
    ```bash
    openclaw onboard --non-interactive \
      --mode local \
      --auth-choice gemini-api-key \
      --gemini-api-key "$GEMINI_API_KEY" \
      --gateway-port 18789 \
      --gateway-bind loopback
    ```
  </Accordion>
  <Accordion title="مثال Z.AI">
    ```bash
    openclaw onboard --non-interactive \
      --mode local \
      --auth-choice zai-api-key \
      --zai-api-key "$ZAI_API_KEY" \
      --gateway-port 18789 \
      --gateway-bind loopback
    ```
  </Accordion>
  <Accordion title="مثال Vercel AI Gateway">
    ```bash
    openclaw onboard --non-interactive \
      --mode local \
      --auth-choice ai-gateway-api-key \
      --ai-gateway-api-key "$AI_GATEWAY_API_KEY" \
      --gateway-port 18789 \
      --gateway-bind loopback
    ```
  </Accordion>
  <Accordion title="مثال Cloudflare AI Gateway">
    ```bash
    openclaw onboard --non-interactive \
      --mode local \
      --auth-choice cloudflare-ai-gateway-api-key \
      --cloudflare-ai-gateway-account-id "your-account-id" \
      --cloudflare-ai-gateway-gateway-id "your-gateway-id" \
      --cloudflare-ai-gateway-api-key "$CLOUDFLARE_AI_GATEWAY_API_KEY" \
      --gateway-port 18789 \
      --gateway-bind loopback
    ```
  </Accordion>
  <Accordion title="مثال Moonshot">
    ```bash
    openclaw onboard --non-interactive \
      --mode local \
      --auth-choice moonshot-api-key \
      --moonshot-api-key "$MOONSHOT_API_KEY" \
      --gateway-port 18789 \
      --gateway-bind loopback
    ```
  </Accordion>
  <Accordion title="مثال Mistral">
    ```bash
    openclaw onboard --non-interactive \
      --mode local \
      --auth-choice mistral-api-key \
      --mistral-api-key "$MISTRAL_API_KEY" \
      --gateway-port 18789 \
      --gateway-bind loopback
    ```
  </Accordion>
  <Accordion title="مثال Synthetic">
    ```bash
    openclaw onboard --non-interactive \
      --mode local \
      --auth-choice synthetic-api-key \
      --synthetic-api-key "$SYNTHETIC_API_KEY" \
      --gateway-port 18789 \
      --gateway-bind loopback
    ```
  </Accordion>
  <Accordion title="مثال OpenCode">
    ```bash
    openclaw onboard --non-interactive \
      --mode local \
      --auth-choice opencode-zen \
      --opencode-zen-api-key "$OPENCODE_API_KEY" \
      --gateway-port 18789 \
      --gateway-bind loopback
    ```
    بدّل إلى `--auth-choice opencode-go --opencode-go-api-key "$OPENCODE_API_KEY"` من أجل فهرس Go.
  </Accordion>
  <Accordion title="مثال Ollama">
    ```bash
    openclaw onboard --non-interactive \
      --mode local \
      --auth-choice ollama \
      --custom-model-id "qwen3.5:27b" \
      --accept-risk \
      --gateway-port 18789 \
      --gateway-bind loopback
    ```
  </Accordion>
  <Accordion title="مثال مزوّد مخصص">
    ```bash
    openclaw onboard --non-interactive \
      --mode local \
      --auth-choice custom-api-key \
      --custom-base-url "https://llm.example.com/v1" \
      --custom-model-id "foo-large" \
      --custom-api-key "$CUSTOM_API_KEY" \
      --custom-provider-id "my-custom" \
      --custom-compatibility anthropic \
      --gateway-port 18789 \
      --gateway-bind loopback
    ```

    `--custom-api-key` اختياري. وإذا حُذف، تتحقق التهيئة من `CUSTOM_API_KEY`.

    صيغة وضع المرجع:

    ```bash
    export CUSTOM_API_KEY="your-key"
    openclaw onboard --non-interactive \
      --mode local \
      --auth-choice custom-api-key \
      --custom-base-url "https://llm.example.com/v1" \
      --custom-model-id "foo-large" \
      --secret-input-mode ref \
      --custom-provider-id "my-custom" \
      --custom-compatibility anthropic \
      --gateway-port 18789 \
      --gateway-bind loopback
    ```

    في هذا الوضع، تخزّن التهيئة `apiKey` بالشكل `{ source: "env", provider: "default", id: "CUSTOM_API_KEY" }`.

  </Accordion>
</AccordionGroup>

ما يزال رمز إعداد Anthropic متاحًا كمسار رمز مدعوم في التهيئة، لكن OpenClaw يفضّل الآن إعادة استخدام Claude CLI عند توفره.
وفي الإنتاج، يُفضَّل استخدام مفتاح API لـ Anthropic.

## إضافة وكيل آخر

استخدم `openclaw agents add <name>` لإنشاء وكيل منفصل له مساحة عمله،
وجلساته، وملفات تعريف المصادقة الخاصة به. يؤدي التشغيل من دون `--workspace` إلى تشغيل المعالج.

```bash
openclaw agents add work \
  --workspace ~/.openclaw/workspace-work \
  --model openai/gpt-5.4 \
  --bind whatsapp:biz \
  --non-interactive \
  --json
```

ما الذي يضبطه:

- `agents.list[].name`
- `agents.list[].workspace`
- `agents.list[].agentDir`

ملاحظات:

- تتبع مساحات العمل الافتراضية النمط `~/.openclaw/workspace-<agentId>`.
- أضف `bindings` لتوجيه الرسائل الواردة (يمكن للمعالج القيام بذلك).
- الأعلام غير التفاعلية: `--model` و `--agent-dir` و `--bind` و `--non-interactive`.

## مستندات ذات صلة

- مركز التهيئة: [التهيئة (CLI)](/ar/start/wizard)
- المرجع الكامل: [مرجع إعداد CLI](/ar/start/wizard-cli-reference)
- مرجع الأوامر: [`openclaw onboard`](/cli/onboard)
