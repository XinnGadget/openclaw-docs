---
title: "Демонстрация проектов"
summary: "Проекты и интеграции, созданные сообществом на базе OpenClaw"
read_when:
  - Ищете реальные примеры использования OpenClaw
  - Обновляете подборку проектов сообщества
---

# Демонстрация проектов

Реальные проекты сообщества. Посмотрите, что люди создают с помощью OpenClaw.

<Info>
**Хотите, чтобы ваш проект был представлен?** Поделитесь им в разделе [#self-promotion в Discord](https://discord.gg/clawd) или отметьте [@openclaw в X](https://x.com/openclaw).
</Info>

## 🎥 OpenClaw в действии

Полное руководство по настройке (28 мин) от VelvetShark.

<div
  style={{
    position: "relative",
    paddingBottom: "56.25%",
    height: 0,
    overflow: "hidden",
    borderRadius: 16,
  }}
>
  <iframe
    src="https://www.youtube-nocookie.com/embed/SaWSPZoPX34"
    title="OpenClaw: локально размещённый ИИ, которым должна была стать Siri (полная настройка)"
    style={{ position: "absolute", top: 0, left: 0, width: "100%", height: "100%" }}
    frameBorder="0"
    loading="lazy"
    allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share"
    allowFullScreen
  />
</div>

[Посмотреть на YouTube](https://www.youtube.com/watch?v=SaWSPZoPX34)

<div
  style={{
    position: "relative",
    paddingBottom: "56.25%",
    height: 0,
    overflow: "hidden",
    borderRadius: 16,
  }}
>
  <iframe
    src="https://www.youtube-nocookie.com/embed/mMSKQvlmFuQ"
    title="Демонстрационное видео OpenClaw"
    style={{ position: "absolute", top: 0, left: 0, width: "100%", height: "100%" }}
    frameBorder="0"
    loading="lazy"
    allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share"
    allowFullScreen
  />
</div>

[Посмотреть на YouTube](https://www.youtube.com/watch?v=mMSKQvlmFuQ)

<div
  style={{
    position: "relative",
    paddingBottom: "56.25%",
    height: 0,
    overflow: "hidden",
    borderRadius: 16,
  }}
>
  <iframe
    src="https://www.youtube-nocookie.com/embed/5kkIJNUGFho"
    title="Демонстрация проектов сообщества OpenClaw"
    style={{ position: "absolute", top: 0, left: 0, width: "100%", height: "100%" }}
    frameBorder="0"
    loading="lazy"
    allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share"
    allowFullScreen
  />
</div>

[Посмотреть на YouTube](https://www.youtube.com/watch?v=5kkIJNUGFho)

## 🆕 Свежие проекты из Discord

<CardGroup cols={2}>

<Card title="Обзор PR → обратная связь в Telegram" icon="code-pull-request" href="https://x.com/i/status/2010878524543131691">
  **@bangnokia** • `review` `github` `telegram`

OpenCode завершает изменения → создаёт PR → OpenClaw анализирует различия и отправляет в Telegram ответ с "незначительными предложениями", а также чётким вердиктом о слиянии (включая критические исправления, которые нужно внести в первую очередь).

  <img src="/assets/showcase/pr-review-telegram.jpg" alt="Обратная связь по PR от OpenClaw в Telegram" />
</Card>

<Card title="Навык для винной карты за несколько минут" icon="wine-glass" href="https://x.com/i/status/2010916352454791216">
  **@prades_maxime** • `skills` `local` `csv`

Запросил у "Robby" (@openclaw) навык для локальной винной карты. Система запрашивает образец экспорта в CSV и место для его хранения, затем быстро создаёт и тестирует навык (в примере — для 962 бутылок).

  <img src="/assets/showcase/wine-cellar-skill.jpg" alt="Создание навыка для локальной винной карты в OpenClaw из CSV" />
</Card>

<Card title="Автопилот для покупок в Tesco" icon="cart-shopping" href="https://x.com/i/status/2009724862470689131">
  **@marchattonhere** • `automation` `browser` `shopping`

Еженедельный план питания → регулярные покупки → бронирование слота для доставки → подтверждение заказа. Без API, только управление браузером.

  <img src="/assets/showcase/tesco-shop.jpg" alt="Автоматизация покупок в Tesco через чат" />
</Card>

<Card title="SNAG: скриншот в Markdown" icon="scissors" href="https://github.com/am-will/snag">
  **@am-will** • `devtools` `screenshots` `markdown`

Выделите область экрана с помощью горячей клавиши → используйте Gemini Vision → мгновенно получите Markdown в буфере обмена.

  <img src="/assets/showcase/snag.png" alt="Инструмент SNAG для преобразования скриншотов в Markdown" />
</Card>

<Card title="Интерфейс для агентов (Agents UI)" icon="window-maximize" href="https://releaseflow.net/kitze/agents-ui">
  **@kitze** • `ui` `skills` `sync`

Десктопное приложение для управления навыками и командами в Agents, Claude, Codex и OpenClaw.

  <img src="/assets/showcase/agents-ui.jpg" alt="Приложение Agents UI" />
</Card>

<Card title="Голосовые заметки в Telegram (papla.media)" icon="microphone" href="https://papla.media/docs">
  **Сообщество** • `voice` `tts` `telegram`

Использует TTS от papla.media и отправляет результаты в виде голосовых заметок в Telegram (без автоматического воспроизведения).

  <img src="/assets/showcase/papla-tts.jpg" alt="Голосовая заметка в Telegram, созданная с помощью TTS" />
</Card>

<Card title="CodexMonitor" icon="eye" href="https://clawhub.ai/odrobnik/codexmonitor">
  **@odrobnik** • `devtools` `codex` `brew`

Помощник, установленный через Homebrew, для просмотра и мониторинга локальных сессий OpenAI Codex (CLI + VS Code).

  <img src="/assets/showcase/codexmonitor.png" alt="CodexMonitor на ClawHub" />
</Card>

<Card title="Управление 3D-принтером Bambu" icon="print" href="https://clawhub.ai/tobiasbischoff/bambu-cli">
  **@tobiasbischoff** • `hardware` `3d-printing` `skill`

Управление и устранение неполадок в принтерах BambuLab: статус, задания, камера, AMS, калибровка и т. д.

  <img src="/assets/showcase/bambu-cli.png" alt="Навык Bambu CLI на ClawHub" />
</Card>

<Card title="Транспорт Вены (Wiener Linien)" icon="train" href="https://clawhub.ai/hjanuschka/wienerlinien">
  **@hjanuschka** • `travel` `transport` `skill`

Информация о времени отправления, сбоях, состоянии лифтов и маршрутах общественного транспорта Вены в режиме реального времени.

  <img src="/assets/showcase/wienerlinien.png" alt="Навык Wiener Linien на ClawHub" />
</Card>

<Card title="Бронирование школьных обедов в ParentPay" icon="utensils" href="#">
  **@George5562** • `automation` `browser` `parenting`

Автоматизированное бронирование школьных обедов в Великобритании через ParentPay. Использует координаты мыши для надёжного клика по ячейкам таблицы.