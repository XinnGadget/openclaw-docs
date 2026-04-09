---
title: "Alibaba Model Studio"
summary: "Генерация видео Alibaba Wan в OpenClaw"
read_when:
  - Вы хотите использовать генерацию видео Alibaba Wan в OpenClaw
  - Вам нужно настроить ключ API Model Studio или DashScope для генерации видео
---

# Alibaba Model Studio

OpenClaw включает встроенного провайдера генерации видео `alibaba` для моделей Wan в Alibaba Model Studio / DashScope.

- Провайдер: `alibaba`
- Предпочтительный способ аутентификации: `MODELSTUDIO_API_KEY`
- Также принимаются: `DASHSCOPE_API_KEY`, `QWEN_API_KEY`
- API: асинхронная генерация видео в DashScope / Model Studio

## Быстрый старт

1. Установите ключ API:

```bash
openclaw onboard --auth-choice qwen-standard-api-key
```

2. Установите модель видео по умолчанию:

```json5
{
  agents: {
    defaults: {
      videoGenerationModel: {
        primary: "alibaba/wan2.6-t2v",
      },
    },
  },
}
```

## Встроенные модели Wan

Встроенный провайдер `alibaba` в настоящее время регистрирует следующие модели:

- `alibaba/wan2.6-t2v`
- `alibaba/wan2.6-i2v`
- `alibaba/wan2.6-r2v`
- `alibaba/wan2.6-r2v-flash`
- `alibaba/wan2.7-r2v`

## Текущие ограничения

- До **1** выходного видео на запрос
- До **1** входного изображения
- До **4** входных видео
- Длительность до **10 секунд**
- Поддерживаются параметры `size`, `aspectRatio`, `resolution`, `audio` и `watermark`
- Для режима эталонного изображения/видео в настоящее время требуются **удалённые URL по протоколу http(s)**

## Связь с Qwen

Встроенный провайдер `qwen` также использует конечные точки DashScope, размещённые на Alibaba, для генерации видео Wan. Используйте:

- `qwen/...`, если вам нужен стандартный провайдер Qwen
- `alibaba/...`, если вам нужен прямой доступ к поверхности генерации видео Wan от поставщика

## Связанные материалы

- [Генерация видео](/tools/video-generation)
- [Qwen](/providers/qwen)
- [Справочник по конфигурации](/gateway/configuration-reference#agent-defaults)