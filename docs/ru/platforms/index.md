---
summary: "Обзор поддержки платформ (Gateway + сопутствующие приложения)"
read_when:
  - Ищете информацию о поддержке ОС или путях установки
  - Принимаете решение, где запустить Gateway
title: "Платформы"
---

# Платформы

Ядро OpenClaw написано на TypeScript. **В качестве среды выполнения рекомендуется использовать Node.**
Использование Bun для Gateway не рекомендуется (ошибки в WhatsApp/Telegram).

Сопутствующие приложения существуют для macOS (приложение в строке меню) и мобильных узлов (iOS/Android). Приложения для Windows и Linux планируются, но Gateway уже полностью поддерживается.
Также планируется выпуск нативных сопутствующих приложений для Windows; для запуска Gateway рекомендуется использовать WSL2.

## Выберите свою ОС

- macOS: [macOS](/platforms/macos)
- iOS: [iOS](/platforms/ios)
- Android: [Android](/platforms/android)
- Windows: [Windows](/platforms/windows)
- Linux: [Linux](/platforms/linux)

## VPS и хостинг

- Хаб VPS: [VPS хостинг](/vps)
- Fly.io: [Fly.io](/install/fly)
- Hetzner (Docker): [Hetzner](/install/hetzner)
- GCP (Compute Engine): [GCP](/install/gcp)
- Azure (Linux VM): [Azure](/install/azure)
- exe.dev (VM + HTTPS-прокси): [exe.dev](/install/exe-dev)

## Общие ссылки

- Руководство по установке: [Начало работы](/start/getting-started)
- Руководство по работе с Gateway: [Gateway](/gateway)
- Настройка Gateway: [Конфигурация](/gateway/configuration)
- Статус службы: `openclaw gateway status`

## Установка службы Gateway (CLI)

Используйте один из следующих способов (все поддерживаются):

- Мастер (рекомендуется): `openclaw onboard --install-daemon`
- Прямой способ: `openclaw gateway install`
- Настройка потока: `openclaw configure` → выберите **Gateway service**
- Восстановление/миграция: `openclaw doctor` (предлагает установить или исправить службу)

Целевая служба зависит от ОС:

- macOS: LaunchAgent (`ai.openclaw.gateway` или `ai.openclaw.<profile>`; устаревший вариант — `com.openclaw.*`)
- Linux/WSL2: пользовательская служба systemd (`openclaw-gateway[-<profile>].service`)
- Нативная Windows: запланированная задача (`OpenClaw Gateway` или `OpenClaw Gateway (<profile>)`), с резервным вариантом в виде элемента автозагрузки в папке "Автозагрузка" для каждого пользователя, если создание задачи отклонено