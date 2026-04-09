---
summary: "Панель Canvas, управляемая агентом, внедрённая через WKWebView + пользовательская схема URL"
read_when:
  - Реализация панели Canvas в macOS
  - Добавление элементов управления агентом для визуального рабочего пространства
  - Отладка загрузки Canvas в WKWebView
title: "Canvas"
---

# Canvas (приложение для macOS)

Приложение для macOS встраивает управляемую агентом **панель Canvas** с помощью `WKWebView`. Это лёгкое визуальное рабочее пространство для HTML/CSS/JS, A2UI и небольших интерактивных элементов интерфейса.

## Где располагается Canvas

Состояние Canvas хранится в разделе Application Support:

- `~/Library/Application Support/OpenClaw/canvas/<session>/...`

Панель Canvas предоставляет доступ к этим файлам через **пользовательскую схему URL**:

- `openclaw-canvas://<session>/<path>`

Примеры:

- `openclaw-canvas://main/` → `<canvasRoot>/main/index.html`
- `openclaw-canvas://main/assets/app.css` → `<canvasRoot>/main/assets/app.css`
- `openclaw-canvas://main/widgets/todo/` → `<canvasRoot>/main/widgets/todo/index.html`

Если в корне отсутствует файл `index.html`, приложение отображает **встроенную шаблонную страницу**.

## Поведение панели

- Панель без границ, с возможностью изменения размера, закреплённая рядом с панелью меню (или курсором мыши).
- Запоминает размер и положение для каждой сессии.
- Автоматически перезагружается при изменении локальных файлов Canvas.
- Одновременно видна только одна панель Canvas (сессии переключаются по мере необходимости).

Canvas можно отключить в настройках через пункт **Allow Canvas**. При отключении команды узла Canvas возвращают `CANVAS_DISABLED`.

## Интерфейс API агента

Canvas доступен через **Gateway WebSocket**, благодаря чему агент может:

- показывать/скрывать панель;
- переходить по пути или URL;
- выполнять JavaScript;
- делать снимок экрана.

Примеры использования CLI:

```bash
openclaw nodes canvas present --node <id>
openclaw nodes canvas navigate --node <id> --url "/"
openclaw nodes canvas eval --node <id> --js "document.title"
openclaw nodes canvas snapshot --node <id>
```

Примечания:

- `canvas.navigate` принимает **локальные пути Canvas**, URL по протоколу `http(s)` и URL по схеме `file://`.
- Если передать `"/"`, Canvas отобразит локальную шаблонную страницу или `index.html`.

## A2UI в Canvas

A2UI размещается на хосте Gateway canvas и отображается внутри панели Canvas. Когда Gateway анонсирует хост Canvas, приложение для macOS автоматически переходит на страницу хоста A2UI при первом открытии.

URL хоста A2UI по умолчанию:

```
http://<gateway-host>:18789/__openclaw__/a2ui/
```

### Команды A2UI (v0.8)

В настоящее время Canvas принимает сообщения сервера → клиента **A2UI v0.8**:

- `beginRendering`
- `surfaceUpdate`
- `dataModelUpdate`
- `deleteSurface`

Команда `createSurface` (v0.9) не поддерживается.

Пример использования CLI:

```bash
cat > /tmp/a2ui-v0.8.jsonl <<'EOFA2'
{"surfaceUpdate":{"surfaceId":"main","components":[{"id":"root","component":{"Column":{"children":{"explicitList":["title","content"]}}}},{"id":"title","component":{"Text":{"text":{"literalString":"Canvas (A2UI v0.8)"},"usageHint":"h1"}}},{"id":"content","component":{"Text":{"text":{"literalString":"If you can read this, A2UI push works."},"usageHint":"body"}}}]}}
{"beginRendering":{"surfaceId":"main","root":"root"}}
EOFA2

openclaw nodes canvas a2ui push --jsonl /tmp/a2ui-v0.8.jsonl --node <id>
```

Быстрая проверка работоспособности:

```bash
openclaw nodes canvas a2ui push --node <id> --text "Hello from A2UI"
```

## Запуск работы агента из Canvas

Canvas может запускать новые сеансы работы агента через глубокие ссылки:

- `openclaw://agent?...`

Пример (на JS):

```js
window.location.href = "openclaw://agent?message=Review%20this%20design";
```

Приложение запрашивает подтверждение, если не предоставлен действительный ключ.

## Примечания по безопасности

- Схема Canvas блокирует обход каталогов; файлы должны находиться в корне сессии.
- Локальный контент Canvas использует пользовательскую схему (сервер loopback не требуется).
- Внешние URL по протоколу `http(s)` разрешены только при явном переходе.