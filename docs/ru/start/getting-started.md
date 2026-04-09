---
summary: "Установите OpenClaw и запустите свой первый чат за несколько минут".
read_when:
  - Первая настройка с нуля
  - Вам нужен самый быстрый способ получить работающий чат
title: "Начало работы"
---

# Начало работы

Установите OpenClaw, запустите процесс первоначальной настройки и пообщайтесь с вашим ИИ-ассистентом — всё примерно за 5 минут. В конце у вас будет работающий Gateway, настроенная аутентификация и активная сессия чата.

## Что вам понадобится

- **Node.js** — рекомендуется Node 24 (также поддерживается Node 22.14+)
- **API-ключ** от поставщика моделей (Anthropic, OpenAI, Google и т. д.) — система запросит его во время первоначальной настройки

<Tip>
Проверьте версию Node с помощью команды `node --version`.
**Пользователи Windows:** поддерживаются как родная среда Windows, так и WSL2. WSL2 более стабильна и рекомендуется для полноценного использования. См. [Windows](/platforms/windows).
Нужно установить Node? См. [Настройка Node](/install/node).
</Tip>

## Быстрая настройка

<Steps>
  <Step title="Установите OpenClaw">
    <Tabs>
      <Tab title="macOS / Linux">
        ```bash
        curl -fsSL https://openclaw.ai/install.sh | bash
        ```
        <img
  src="/assets/install-script.svg"
  alt="Процесс выполнения скрипта установки"
  className="rounded-lg"
/>
      </Tab>
      <Tab title="Windows (PowerShell)">
        ```powershell
        iwr -useb https://openclaw.ai/install.ps1 | iex
        ```
      </Tab>
    </Tabs>

    <Note>
    Другие способы установки (Docker, Nix, npm): [Установка](/install).
    </Note>

  </Step>
  <Step title="Запустите процесс первоначальной настройки">
    ```bash
    openclaw onboard --install-daemon
    ```

    Мастер поможет вам выбрать поставщика моделей, задать API-ключ и настроить Gateway. Это займёт около 2 минут.

    См. [Первоначальная настройка (CLI)](/start/wizard) для полного руководства.

  </Step>
  <Step title="Проверьте, что Gateway запущен">
    ```bash
    openclaw gateway status
    ```

    Вы должны увидеть, что Gateway слушает порт 18789.

  </Step>
  <Step title="Откройте панель управления">
    ```bash
    openclaw dashboard
    ```

    Это откроет интерфейс управления (Control UI) в вашем браузере. Если он загрузился, значит, всё работает.

  </Step>
  <Step title="Отправьте своё первое сообщение">
    Введите сообщение в чате интерфейса управления (Control UI), и вы должны получить ответ от ИИ.

    Хотите общаться с телефона? Самый быстрый канал для настройки — [Telegram](/channels/telegram) (потребуется только токен бота). См. [Каналы](/channels) для ознакомления со всеми вариантами.

  </Step>
</Steps>

<Accordion title="Дополнительно: подключите пользовательскую сборку Control UI">
  Если вы поддерживаете локализованную или настроенную сборку панели управления, укажите путь `gateway.controlUi.root` к каталогу, содержащему ваши собранные статические ресурсы и файл `index.html`.

```bash
mkdir -p "$HOME/.openclaw/control-ui-custom"
# Скопируйте собранные статические файлы в этот каталог.
```

Затем задайте:

```json
{
  "gateway": {
    "controlUi": {
      "enabled": true,
      "root": "$HOME/.openclaw/control-ui-custom"
    }
  }
}
```

Перезапустите Gateway и снова откройте панель управления:

```bash
openclaw gateway restart
openclaw dashboard
```

</Accordion>

## Что делать дальше

<Columns>
  <Card title="Подключите канал" href="/channels" icon="message-square">
    Discord, Feishu, iMessage, Matrix, Microsoft Teams, Signal, Slack, Telegram, WhatsApp, Zalo и другие.
  </Card>
  <Card title="Сопряжение и безопасность" href="/channels/pairing" icon="shield">
    Настройте, кто может отправлять сообщения вашему агенту.
  </Card>
  <Card title="Настройте Gateway" href="/gateway/configuration" icon="settings">
    Модели, инструменты, песочница и расширенные настройки.
  </Card>
  <Card title="Ознакомьтесь с инструментами" href="/tools" icon="wrench">
    Браузер, exec, веб-поиск, навыки и плагины.
  </Card>
</Columns>

<Accordion title="Дополнительно: переменные окружения">
  Если вы запускаете OpenClaw как учётную запись службы или хотите использовать пользовательские пути:

- `OPENCLAW_HOME` — домашний каталог для разрешения внутренних путей
- `OPENCLAW_STATE_DIR` — переопределение каталога состояния
- `OPENCLAW_CONFIG_PATH` — переопределение пути к файлу конфигурации

Полное руководство: [Переменные окружения](/help/environment).
</Accordion>