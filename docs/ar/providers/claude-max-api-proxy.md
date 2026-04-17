---
read_when:
    - تريد استخدام اشتراك Claude Max مع أدوات متوافقة مع OpenAI
    - تريد خادم API محليًا يغلّف Claude Code CLI
    - تريد تقييم الوصول إلى Anthropic القائم على الاشتراك مقابل القائم على مفتاح API
summary: وكيل مجتمع لعرض بيانات اعتماد اشتراك Claude كنقطة نهاية متوافقة مع OpenAI
title: Claude Max API Proxy
x-i18n:
    generated_at: "2026-04-12T23:29:59Z"
    model: gpt-5.4
    provider: openai
    source_hash: 534bc3d189e68529fb090258eb0d6db6d367eb7e027ad04b1f0be55f6aa7d889
    source_path: providers/claude-max-api-proxy.md
    workflow: 15
---

# Claude Max API Proxy

`claude-max-api-proxy` هي أداة من المجتمع تعرض اشتراك Claude Max/Pro الخاص بك
كنقطة نهاية API متوافقة مع OpenAI. يتيح لك هذا استخدام اشتراكك مع أي أداة تدعم
تنسيق OpenAI API.

<Warning>
هذا المسار يقتصر على التوافق التقني فقط. فقد سبق أن حظرت Anthropic بعض
استخدامات الاشتراك خارج Claude Code. يجب أن تقرر بنفسك ما إذا كنت تريد استخدامه،
وأن تتحقق من الشروط الحالية لـ Anthropic قبل الاعتماد عليه.
</Warning>

## لماذا قد تستخدم هذا؟

| النهج                    | التكلفة                                              | الأنسب لـ                                 |
| ------------------------ | ---------------------------------------------------- | ----------------------------------------- |
| Anthropic API            | الدفع لكل رمز (~$15/M للإدخال، و$75/M للإخراج لـ Opus) | تطبيقات الإنتاج، والأحجام الكبيرة         |
| اشتراك Claude Max        | $200 شهريًا بسعر ثابت                                | الاستخدام الشخصي، والتطوير، والاستخدام غير المحدود |

إذا كان لديك اشتراك Claude Max وتريد استخدامه مع أدوات متوافقة مع OpenAI، فقد
يخفض هذا الوكيل التكلفة لبعض تدفقات العمل. وتبقى مفاتيح API هي المسار الأوضح من
ناحية السياسة لاستخدامات الإنتاج.

## كيف يعمل

```
تطبيقك ← claude-max-api-proxy ← Claude Code CLI ← Anthropic (عبر الاشتراك)
   (تنسيق OpenAI)                (يحوّل التنسيق)       (يستخدم تسجيل دخولك)
```

يقوم الوكيل بما يلي:

1. يقبل الطلبات بتنسيق OpenAI على `http://localhost:3456/v1/chat/completions`
2. يحولها إلى أوامر Claude Code CLI
3. يعيد الاستجابات بتنسيق OpenAI (مع دعم البث)

## البدء

<Steps>
  <Step title="Install the proxy">
    يتطلب Node.js 20+ وClaude Code CLI.

    ```bash
    npm install -g claude-max-api-proxy

    # تأكد من أن Claude CLI قد تمت مصادقته
    claude --version
    ```

  </Step>
  <Step title="Start the server">
    ```bash
    claude-max-api
    # يعمل الخادم على http://localhost:3456
    ```
  </Step>
  <Step title="Test the proxy">
    ```bash
    # فحص السلامة
    curl http://localhost:3456/health

    # عرض النماذج
    curl http://localhost:3456/v1/models

    # إكمال الدردشة
    curl http://localhost:3456/v1/chat/completions \
      -H "Content-Type: application/json" \
      -d '{
        "model": "claude-opus-4",
        "messages": [{"role": "user", "content": "Hello!"}]
      }'
    ```

  </Step>
  <Step title="Configure OpenClaw">
    وجّه OpenClaw إلى الوكيل كنقطة نهاية مخصصة متوافقة مع OpenAI:

    ```json5
    {
      env: {
        OPENAI_API_KEY: "not-needed",
        OPENAI_BASE_URL: "http://localhost:3456/v1",
      },
      agents: {
        defaults: {
          model: { primary: "openai/claude-opus-4" },
        },
      },
    }
    ```

  </Step>
</Steps>

## النماذج المتاحة

| معرّف النموذج      | يطابق         |
| ------------------ | ------------- |
| `claude-opus-4`    | Claude Opus 4 |
| `claude-sonnet-4`  | Claude Sonnet 4 |
| `claude-haiku-4`   | Claude Haiku 4 |

## متقدم

<AccordionGroup>
  <Accordion title="Proxy-style OpenAI-compatible notes">
    يستخدم هذا المسار أسلوب الوكيل نفسه المتوافق مع OpenAI مثل واجهات `/v1`
    الخلفية المخصصة الأخرى:

    - لا يُطبّق تشكيل الطلبات الأصلي الخاص بـ OpenAI فقط
    - لا يوجد `service_tier`، ولا `store` الخاص بـ Responses، ولا تلميحات لذاكرة
      التخزين المؤقت للمطالبات، ولا تشكيل حمولة متوافق مع OpenAI للاستدلال
    - لا يتم حقن ترويسات الإسناد المخفية الخاصة بـ OpenClaw (`originator` و`version` و`User-Agent`)
      على عنوان URL الخاص بالوكيل

  </Accordion>

  <Accordion title="Auto-start on macOS with LaunchAgent">
    أنشئ LaunchAgent لتشغيل الوكيل تلقائيًا:

    ```bash
    cat > ~/Library/LaunchAgents/com.claude-max-api.plist << 'EOF'
    <?xml version="1.0" encoding="UTF-8"?>
    <!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
    <plist version="1.0">
    <dict>
      <key>Label</key>
      <string>com.claude-max-api</string>
      <key>RunAtLoad</key>
      <true/>
      <key>KeepAlive</key>
      <true/>
      <key>ProgramArguments</key>
      <array>
        <string>/usr/local/bin/node</string>
        <string>/usr/local/lib/node_modules/claude-max-api-proxy/dist/server/standalone.js</string>
      </array>
      <key>EnvironmentVariables</key>
      <dict>
        <key>PATH</key>
        <string>/usr/local/bin:/opt/homebrew/bin:~/.local/bin:/usr/bin:/bin</string>
      </dict>
    </dict>
    </plist>
    EOF

    launchctl bootstrap gui/$(id -u) ~/Library/LaunchAgents/com.claude-max-api.plist
    ```

  </Accordion>
</AccordionGroup>

## الروابط

- **npm:** [https://www.npmjs.com/package/claude-max-api-proxy](https://www.npmjs.com/package/claude-max-api-proxy)
- **GitHub:** [https://github.com/atalovesyou/claude-max-api-proxy](https://github.com/atalovesyou/claude-max-api-proxy)
- **المشكلات:** [https://github.com/atalovesyou/claude-max-api-proxy/issues](https://github.com/atalovesyou/claude-max-api-proxy/issues)

## ملاحظات

- هذه **أداة من المجتمع**، وليست مدعومة رسميًا من Anthropic أو OpenClaw
- تتطلب اشتراك Claude Max/Pro نشطًا مع Claude Code CLI تمت مصادقته
- يعمل الوكيل محليًا ولا يرسل البيانات إلى أي خوادم تابعة لجهات خارجية
- الاستجابات المتدفقة مدعومة بالكامل

<Note>
للتكامل الأصلي مع Anthropic باستخدام Claude CLI أو مفاتيح API، راجع [Anthropic provider](/ar/providers/anthropic). ولاشتراكات OpenAI/Codex، راجع [OpenAI provider](/ar/providers/openai).
</Note>

## ذو صلة

<CardGroup cols={2}>
  <Card title="Anthropic provider" href="/ar/providers/anthropic" icon="bolt">
    تكامل OpenClaw الأصلي مع Claude CLI أو مفاتيح API.
  </Card>
  <Card title="OpenAI provider" href="/ar/providers/openai" icon="robot">
    لاشتراكات OpenAI/Codex.
  </Card>
  <Card title="Model providers" href="/ar/concepts/model-providers" icon="layers">
    نظرة عامة على جميع الموفّرين، ومراجع النماذج، وسلوك التبديل الاحتياطي.
  </Card>
  <Card title="Configuration" href="/ar/gateway/configuration" icon="gear">
    المرجع الكامل للإعدادات.
  </Card>
</CardGroup>
