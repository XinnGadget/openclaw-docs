---
read_when:
    - اقتران عقدة iOS أو إعادة توصيلها
    - تشغيل تطبيق iOS من المصدر
    - تصحيح اكتشاف البوابة أو أوامر canvas
summary: 'تطبيق iOS للعقدة: الاتصال بالبوابة، والاقتران، وcanvas، واستكشاف الأخطاء وإصلاحها'
title: تطبيق iOS
x-i18n:
    generated_at: "2026-04-07T07:18:43Z"
    model: gpt-5.4
    provider: openai
    source_hash: f3e0a6e33e72d4c9f1f17ef70a1b67bae9ebe4a2dca16677ea6b28d0ddac1b4e
    source_path: platforms/ios.md
    workflow: 15
---

# تطبيق iOS (العقدة)

التوفّر: معاينة داخلية. لم يُوزَّع تطبيق iOS علنًا بعد.

## ما الذي يفعله

- يتصل ببوابة عبر WebSocket ‏(LAN أو tailnet).
- يوفّر قدرات العقدة: Canvas، ولقطة شاشة، والتقاط الكاميرا، والموقع، ووضع التحدث، والتنبيه الصوتي.
- يستقبل أوامر `node.invoke` ويبلّغ عن أحداث حالة العقدة.

## المتطلبات

- تشغيل البوابة على جهاز آخر (macOS أو Linux أو Windows عبر WSL2).
- مسار الشبكة:
  - نفس LAN عبر Bonjour، **أو**
  - Tailnet عبر unicast DNS-SD ‏(مثال على النطاق: `openclaw.internal.`)، **أو**
  - مضيف/منفذ يدويان (احتياطي).

## البدء السريع (اقتران + اتصال)

1. ابدأ تشغيل البوابة:

```bash
openclaw gateway --port 18789
```

2. في تطبيق iOS، افتح Settings واختر بوابة مكتشفة (أو فعّل Manual Host وأدخل المضيف/المنفذ).

3. وافق على طلب الاقتران على مضيف البوابة:

```bash
openclaw devices list
openclaw devices approve <requestId>
```

إذا أعاد التطبيق محاولة الاقتران بتفاصيل مصادقة متغيرة (الدور/النطاقات/المفتاح العام)،
فسيتم استبدال الطلب المعلّق السابق وسيُنشأ `requestId` جديد.
شغّل `openclaw devices list` مرة أخرى قبل الموافقة.

4. تحقّق من الاتصال:

```bash
openclaw nodes status
openclaw gateway call node.list --params "{}"
```

## الإشعارات الفورية المعتمدة على relay للبنيات الرسمية

تستخدم بنيات iOS الرسمية الموزعة relay إشعارات خارجيًا بدلًا من نشر
رمز APNs الخام إلى البوابة.

متطلب جهة البوابة:

```json5
{
  gateway: {
    push: {
      apns: {
        relay: {
          baseUrl: "https://relay.example.com",
        },
      },
    },
  },
}
```

كيف يعمل التدفق:

- يسجّل تطبيق iOS نفسه لدى relay باستخدام App Attest وإيصال التطبيق.
- يعيد relay مقبض relay معتمًا بالإضافة إلى إذن إرسال ضمن نطاق التسجيل.
- يجلب تطبيق iOS هوية البوابة المقترنة ويضمّنها في تسجيل relay، بحيث يُفوَّض التسجيل المعتمد على relay إلى تلك البوابة المحددة.
- يمرّر التطبيق هذا التسجيل المعتمد على relay إلى البوابة المقترنة عبر `push.apns.register`.
- تستخدم البوابة مقبض relay المخزن هذا لأوامر `push.test` وعمليات الإيقاظ في الخلفية والتنبيهات.
- يجب أن يطابق عنوان URL الأساسي لـ relay في البوابة عنوان URL الخاص بـ relay المضمّن في بنية iOS الرسمية/TestFlight.
- إذا اتصل التطبيق لاحقًا ببوابة مختلفة أو ببنية ذات عنوان URL أساسي مختلف لـ relay، فسيحدّث تسجيل relay بدلًا من إعادة استخدام الربط القديم.

ما الذي **لا** تحتاجه البوابة لهذا المسار:

- لا حاجة إلى رمز relay على مستوى النشر.
- لا حاجة إلى مفتاح APNs مباشر لعمليات الإرسال الرسمية/TestFlight المعتمدة على relay.

تدفق التشغيل المتوقع:

1. ثبّت بنية iOS الرسمية/TestFlight.
2. عيّن `gateway.push.apns.relay.baseUrl` على البوابة.
3. اقترن التطبيق بالبوابة ودعه يُكمل الاتصال.
4. ينشر التطبيق `push.apns.register` تلقائيًا بعد أن يحصل على رمز APNs، ويتصل جلسة المشغّل، وينجح تسجيل relay.
5. بعد ذلك، يمكن لأوامر `push.test` وعمليات إيقاظ إعادة الاتصال والتنبيهات استخدام التسجيل المخزن المعتمد على relay.

ملاحظة التوافق:

- ما يزال `OPENCLAW_APNS_RELAY_BASE_URL` يعمل كتجاوز مؤقت لمتغير البيئة للبوابة.

## تدفق المصادقة والثقة

يوجد relay لفرض قيدين لا يستطيع مسار APNs المباشر إلى البوابة توفيرهما
لبنيات iOS الرسمية:

- لا يمكن إلا لبنيات OpenClaw iOS الأصلية الموزعة عبر Apple استخدام relay المستضاف.
- لا يمكن للبوابة إرسال إشعارات معتمدة على relay إلا إلى أجهزة iOS التي اقترنت بتلك
  البوابة تحديدًا.

بالتفصيل لكل قفزة:

1. `iOS app -> gateway`
   - يقترن التطبيق أولًا بالبوابة عبر تدفق مصادقة البوابة المعتاد.
   - يمنح ذلك التطبيق جلسة عقدة موثقة بالإضافة إلى جلسة مشغّل موثقة.
   - تُستخدم جلسة المشغّل لاستدعاء `gateway.identity.get`.

2. `iOS app -> relay`
   - يستدعي التطبيق نقاط نهاية تسجيل relay عبر HTTPS.
   - يتضمن التسجيل برهان App Attest بالإضافة إلى إيصال التطبيق.
   - يتحقق relay من معرّف الحزمة، وبرهان App Attest، وإيصال Apple، ويتطلب
     مسار التوزيع الرسمي/الإنتاجي.
   - هذا ما يمنع بنيات Xcode/التطوير المحلية من استخدام relay المستضاف. قد تكون البنية المحلية
     موقّعة، لكنها لا تستوفي برهان التوزيع الرسمي من Apple الذي يتوقعه relay.

3. `gateway identity delegation`
   - قبل تسجيل relay، يجلب التطبيق هوية البوابة المقترنة من
     `gateway.identity.get`.
   - يضمّن التطبيق هوية البوابة هذه في حمولة تسجيل relay.
   - يعيد relay مقبض relay وإذن إرسال ضمن نطاق التسجيل يكونان مفوّضين إلى
     هوية البوابة تلك.

4. `gateway -> relay`
   - تخزن البوابة مقبض relay وإذن الإرسال القادمين من `push.apns.register`.
   - عند `push.test` وعمليات إيقاظ إعادة الاتصال والتنبيهات، توقّع البوابة طلب الإرسال
     بهوية جهازها الخاصة.
   - يتحقق relay من كل من إذن الإرسال المخزن وتوقيع البوابة مقابل
     هوية البوابة المفوّضة من التسجيل.
   - لا يمكن لبوابة أخرى إعادة استخدام ذلك التسجيل المخزن، حتى لو حصلت بطريقة ما على المقبض.

5. `relay -> APNs`
   - يمتلك relay بيانات اعتماد APNs الإنتاجية ورمز APNs الخام للبنية الرسمية.
   - لا تخزّن البوابة رمز APNs الخام للبنيات الرسمية المعتمدة على relay.
   - يرسل relay الإشعار النهائي إلى APNs نيابةً عن البوابة المقترنة.

سبب إنشاء هذا التصميم:

- لإبقاء بيانات اعتماد APNs الإنتاجية خارج بوابات المستخدمين.
- لتجنب تخزين رموز APNs الخام للبنيات الرسمية على البوابة.
- للسماح باستخدام relay المستضاف فقط لبنيات OpenClaw الرسمية/TestFlight.
- لمنع بوابة واحدة من إرسال إشعارات إيقاظ إلى أجهزة iOS مملوكة لبوابة مختلفة.

تبقى البنيات المحلية/اليدوية على APNs المباشر. إذا كنت تختبر هذه البنيات من دون relay، فلا تزال
البوابة تحتاج إلى بيانات اعتماد APNs مباشرة:

```bash
export OPENCLAW_APNS_TEAM_ID="TEAMID"
export OPENCLAW_APNS_KEY_ID="KEYID"
export OPENCLAW_APNS_PRIVATE_KEY_P8="$(cat /path/to/AuthKey_KEYID.p8)"
```

هذه متغيرات بيئة وقت تشغيل على مضيف البوابة، وليست إعدادات Fastlane. يخزن `apps/ios/fastlane/.env` فقط
مصادقة App Store Connect / TestFlight مثل `ASC_KEY_ID` و `ASC_ISSUER_ID`; ولا يهيئ
تسليم APNs المباشر لبنيات iOS المحلية.

التخزين الموصى به على مضيف البوابة:

```bash
mkdir -p ~/.openclaw/credentials/apns
chmod 700 ~/.openclaw/credentials/apns
mv /path/to/AuthKey_KEYID.p8 ~/.openclaw/credentials/apns/AuthKey_KEYID.p8
chmod 600 ~/.openclaw/credentials/apns/AuthKey_KEYID.p8
export OPENCLAW_APNS_PRIVATE_KEY_PATH="$HOME/.openclaw/credentials/apns/AuthKey_KEYID.p8"
```

لا تقم بعمل commit لملف `.p8` ولا تضعه داخل نسخة المستودع المحلية.

## مسارات الاكتشاف

### Bonjour ‏(LAN)

يستعرض تطبيق iOS الخدمة `_openclaw-gw._tcp` على `local.` وعند التهيئة، يستعرض أيضًا
نطاق اكتشاف wide-area DNS-SD نفسه. تظهر البوابات الموجودة على نفس LAN تلقائيًا من `local.`;
ويمكن للاكتشاف عبر الشبكات استخدام النطاق واسع النطاق المهيأ من دون تغيير نوع beacon.

### Tailnet ‏(عبر الشبكات)

إذا كان mDNS محجوبًا، فاستخدم منطقة unicast DNS-SD ‏(اختر نطاقًا؛ مثال:
`openclaw.internal.`) وTailscale split DNS.
راجع [Bonjour](/ar/gateway/bonjour) للحصول على مثال CoreDNS.

### مضيف/منفذ يدويان

في Settings، فعّل **Manual Host** وأدخل مضيف البوابة + المنفذ (الافتراضي `18789`).

## Canvas + A2UI

تعرض عقدة iOS لوحة canvas عبر WKWebView. استخدم `node.invoke` للتحكم بها:

```bash
openclaw nodes invoke --node "iOS Node" --command canvas.navigate --params '{"url":"http://<gateway-host>:18789/__openclaw__/canvas/"}'
```

ملاحظات:

- يقدّم مضيف canvas في البوابة المسارين `/__openclaw__/canvas/` و `/__openclaw__/a2ui/`.
- يتم تقديمه من خادم HTTP الخاص بالبوابة (المنفذ نفسه مثل `gateway.port`، والافتراضي `18789`).
- تنتقل عقدة iOS تلقائيًا إلى A2UI عند الاتصال عندما يُعلن عن عنوان URL لمضيف canvas.
- للعودة إلى البنية المضمنة، استخدم `canvas.navigate` مع `{"url":""}`.

### تقييم canvas / لقطة

```bash
openclaw nodes invoke --node "iOS Node" --command canvas.eval --params '{"javaScript":"(() => { const {ctx} = window.__openclaw; ctx.clearRect(0,0,innerWidth,innerHeight); ctx.lineWidth=6; ctx.strokeStyle=\"#ff2d55\"; ctx.beginPath(); ctx.moveTo(40,40); ctx.lineTo(innerWidth-40, innerHeight-40); ctx.stroke(); return \"ok\"; })()"}'
```

```bash
openclaw nodes invoke --node "iOS Node" --command canvas.snapshot --params '{"maxWidth":900,"format":"jpeg"}'
```

## التنبيه الصوتي + وضع التحدث

- يتوفر التنبيه الصوتي ووضع التحدث في Settings.
- قد يعلّق iOS الصوت في الخلفية؛ لذا اعتبر ميزات الصوت أفضل جهد عندما لا يكون التطبيق نشطًا.

## الأخطاء الشائعة

- `NODE_BACKGROUND_UNAVAILABLE`: اجلب تطبيق iOS إلى الواجهة الأمامية (تتطلب أوامر canvas/الكاميرا/الشاشة ذلك).
- `A2UI_HOST_NOT_CONFIGURED`: لم تعلن البوابة عن عنوان URL لمضيف canvas؛ تحقق من `canvasHost` في [إعدادات البوابة](/ar/gateway/configuration).
- لا يظهر طلب الاقتران مطلقًا: شغّل `openclaw devices list` ووافق يدويًا.
- تفشل إعادة الاتصال بعد إعادة التثبيت: تم مسح رمز الاقتران في Keychain؛ أعد اقتران العقدة.

## مستندات ذات صلة

- [الاقتران](/ar/channels/pairing)
- [الاكتشاف](/ar/gateway/discovery)
- [Bonjour](/ar/gateway/bonjour)
