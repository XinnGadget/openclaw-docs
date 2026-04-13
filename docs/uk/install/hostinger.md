---
read_when:
    - Налаштування OpenClaw на Hostinger
    - Шукаєте керований VPS для OpenClaw
    - Використання OpenClaw 1-Click від Hostinger
summary: Розмістіть OpenClaw на Hostinger
title: Hostinger
x-i18n:
    generated_at: "2026-04-13T13:14:20Z"
    model: gpt-5.4
    provider: openai
    source_hash: cf173cdcf6344f8ee22e839a27f4e063a3a102186f9acc07c4a33d4794e2c034
    source_path: install/hostinger.md
    workflow: 15
---

# Hostinger

Запустіть постійний Gateway OpenClaw на [Hostinger](https://www.hostinger.com/openclaw) через кероване розгортання **1-Click** або встановлення на **VPS**.

## Передумови

- Обліковий запис Hostinger ([реєстрація](https://www.hostinger.com/openclaw))
- Близько 5-10 хвилин

## Варіант A: OpenClaw 1-Click

Найшвидший спосіб почати. Hostinger бере на себе інфраструктуру, Docker і автоматичні оновлення.

<Steps>
  <Step title="Придбайте та запустіть">
    1. На сторінці [Hostinger OpenClaw](https://www.hostinger.com/openclaw) виберіть план Managed OpenClaw і завершіть оформлення замовлення.

    <Note>
    Під час оформлення замовлення ви можете вибрати кредити **Ready-to-Use AI**, які попередньо купуються та миттєво інтегруються в OpenClaw — жодних зовнішніх облікових записів або API-ключів від інших провайдерів не потрібно. Ви можете одразу почати спілкування. Або ж під час налаштування вкажіть власний ключ від Anthropic, OpenAI, Google Gemini чи xAI.
    </Note>

  </Step>

  <Step title="Виберіть канал обміну повідомленнями">
    Виберіть один або кілька каналів для підключення:

    - **WhatsApp** -- відскануйте QR-код, показаний у майстрі налаштування.
    - **Telegram** -- вставте токен бота з [BotFather](https://t.me/BotFather).

  </Step>

  <Step title="Завершіть установлення">
    Натисніть **Finish**, щоб розгорнути інстанс. Щойно все буде готово, відкрийте панель керування OpenClaw з розділу **OpenClaw Overview** у hPanel.
  </Step>

</Steps>

## Варіант B: OpenClaw на VPS

Більше контролю над вашим сервером. Hostinger розгортає OpenClaw через Docker на вашому VPS, а ви керуєте ним через **Docker Manager** у hPanel.

<Steps>
  <Step title="Придбайте VPS">
    1. На сторінці [Hostinger OpenClaw](https://www.hostinger.com/openclaw) виберіть план OpenClaw on VPS і завершіть оформлення замовлення.

    <Note>
    Під час оформлення замовлення ви можете вибрати кредити **Ready-to-Use AI** — вони попередньо купуються та миттєво інтегруються в OpenClaw, тож ви можете почати спілкування без жодних зовнішніх облікових записів або API-ключів від інших провайдерів.
    </Note>

  </Step>

  <Step title="Налаштуйте OpenClaw">
    Коли VPS буде підготовлено, заповніть поля конфігурації:

    - **Gateway token** -- створюється автоматично; збережіть його для подальшого використання.
    - **WhatsApp number** -- ваш номер із кодом країни (необов’язково).
    - **Telegram bot token** -- від [BotFather](https://t.me/BotFather) (необов’язково).
    - **API keys** -- потрібні лише в тому разі, якщо ви не вибрали кредити Ready-to-Use AI під час оформлення замовлення.

  </Step>

  <Step title="Запустіть OpenClaw">
    Натисніть **Deploy**. Після запуску відкрийте панель керування OpenClaw з hPanel, натиснувши **Open**.
  </Step>

</Steps>

Журнали, перезапуски та оновлення керуються безпосередньо з інтерфейсу Docker Manager у hPanel. Щоб оновити, натисніть **Update** у Docker Manager — це завантажить найновіший образ.

## Перевірте налаштування

Надішліть "Hi" своєму помічнику в підключеному каналі. OpenClaw відповість і проведе вас через початкові налаштування.

## Усунення несправностей

**Панель керування не завантажується** -- Зачекайте кілька хвилин, поки контейнер завершить підготовку. Перевірте журнали Docker Manager у hPanel.

**Контейнер Docker постійно перезапускається** -- Відкрийте журнали Docker Manager і перевірте, чи немає помилок конфігурації (відсутні токени, недійсні API-ключі).

**Бот Telegram не відповідає** -- Надішліть повідомлення з кодом сполучення з Telegram безпосередньо як повідомлення в чаті OpenClaw, щоб завершити підключення.

## Наступні кроки

- [Канали](/uk/channels) -- підключіть Telegram, WhatsApp, Discord та інші
- [Конфігурація Gateway](/uk/gateway/configuration) -- усі параметри конфігурації
